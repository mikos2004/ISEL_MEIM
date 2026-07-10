// lib/screens/settings_screen.dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:file_picker/file_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'package:shared_preferences/shared_preferences.dart';

/// Settings screen for configuring alarm PIN and sound.
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: const Text('Settings', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
      ),
      body: const SettingsBody(),
    );
  }
}

class SettingsBody extends StatefulWidget {
  const SettingsBody({super.key});

  @override
  State<SettingsBody> createState() => _SettingsBodyState();
}

class _SettingsBodyState extends State<SettingsBody> {
  bool _obscurePin = true;
  String _selectedSound = 'sound1.wav';
  String _selectedPin = '1234567';
  final AudioPlayer _audioPlayer = AudioPlayer();
  List<Map<String, String>> _importedSounds = [];

  @override
  void initState() {
    super.initState();
    _loadSettings();
    _loadImportedSounds();
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  /// Loads saved settings from SharedPreferences.
  Future<void> _loadSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedPin = prefs.getString('alarm_pin');
      final savedSound = prefs.getString('alarm_sound');
      
      setState(() {
        if (savedPin != null) _selectedPin = savedPin;
        if (savedSound != null) _selectedSound = savedSound;
      });
    } catch (e) {
      debugPrint('Error loading settings: $e');
    }
  }

  /// Saves PIN to SharedPreferences.
  Future<void> _savePin(String pin) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('alarm_pin', pin);
    } catch (e) {
      debugPrint('Error saving PIN: $e');
    }
  }

  /// Saves sound preference to SharedPreferences.
  Future<void> _saveSound(String soundPath) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('alarm_sound', soundPath);
    } catch (e) {
      debugPrint('Error saving sound: $e');
    }
  }

  /// Loads imported sounds from app storage.
  Future<void> _loadImportedSounds() async {
    try {
      final appDir = await getApplicationDocumentsDirectory();
      final soundsDir = Directory(path.join(appDir.path, 'imported_sounds'));
      
      if (await soundsDir.exists()) {
        final files = await soundsDir.list().toList();
        final List<Map<String, String>> sounds = [];
        
        for (var file in files) {
          if (file is File && (file.path.endsWith('.mp3') || file.path.endsWith('.wav') || file.path.endsWith('.m4a'))) {
            sounds.add({
              'file': file.path,
              'label': path.basename(file.path),
            });
          }
        }
        
        setState(() => _importedSounds = sounds);
      }
    } catch (e) {
      debugPrint('Error loading imported sounds: $e');
    }
  }

  /// Copies imported audio file to app storage.
  Future<String?> _copyFileToAppStorage(String filePath) async {
    try {
      final appDir = await getApplicationDocumentsDirectory();
      final soundsDir = Directory(path.join(appDir.path, 'imported_sounds'));
      
      if (!await soundsDir.exists()) {
        await soundsDir.create(recursive: true);
      }
      
      final fileName = path.basename(filePath);
      final newPath = path.join(soundsDir.path, fileName);
      final newFile = File(newPath);
      
      if (await newFile.exists()) {
        final nameWithoutExt = path.basenameWithoutExtension(fileName);
        final extension = path.extension(fileName);
        final timestamp = DateTime.now().millisecondsSinceEpoch;
        final uniqueFileName = '${nameWithoutExt}_$timestamp$extension';
        final uniquePath = path.join(soundsDir.path, uniqueFileName);
        await File(filePath).copy(uniquePath);
        return uniquePath;
      } else {
        await File(filePath).copy(newPath);
        return newPath;
      }
    } catch (e) {
      debugPrint('Error copying file: $e');
      return null;
    }
  }

  /// Imports audio file from device storage.
  Future<void> _importAudioFromDevice() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.audio,
        allowMultiple: false,
        withData: false,
      );

      if (result != null && result.files.isNotEmpty) {
        final pickedFile = result.files.first.path;
        
        if (pickedFile != null) {
          if (!context.mounted) return;
          
          showDialog(
            context: context,
            barrierDismissible: false,
            builder: (context) => const AlertDialog(
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('A importar o áudio...'),
                ],
              ),
            ),
          );

          final savedPath = await _copyFileToAppStorage(pickedFile);
          
          if (context.mounted) Navigator.pop(context);

          if (savedPath != null) {
            await _loadImportedSounds();
            setState(() => _selectedSound = savedPath);
            await _saveSound(savedPath);
            
            if (context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Áudio improtado com sucesso'),
                  backgroundColor: Colors.green,
                  duration: Duration(seconds: 2),
                ),
              );
            }
          }
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erro ao importar o áudio: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Deletes an imported sound file.
  Future<void> _deleteImportedSound(String filePath, String label) async {
    try {
      final file = File(filePath);
      if (await file.exists()) {
        await file.delete();
        await _loadImportedSounds();
        
        if (_selectedSound == filePath) {
          setState(() => _selectedSound = 'sound1.wav');
          await _saveSound('sound1.wav');
        }
        
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('"$label" eliminado com sucesso'),
              backgroundColor: Colors.orange,
            ),
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erro a eliminar o áudio: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Plays a preview of the selected sound.
  Future<void> _playSoundPreview(String soundPath, bool isAsset) async {
    try {
      await _audioPlayer.stop();
      
      if (isAsset) {
        await _audioPlayer.play(AssetSource('sounds/$soundPath'));
      } else {
        await _audioPlayer.play(DeviceFileSource(soundPath));
      }
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('A tocar amostra...'),
            duration: Duration(seconds: 1),
          ),
        );
      }
    } catch (e) {
      debugPrint('Erro a tocar amostra: $e');
    }
  }

  /// Shows PIN change dialog.
  void _showPinOptions() {
    final TextEditingController currentPinController = TextEditingController();
    final TextEditingController newPinController = TextEditingController();
    final TextEditingController confirmPinController = TextEditingController();
    int step = 1;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setStateDialog) {
            return AlertDialog(
              backgroundColor: const Color(0xFFE0F3FF),
              title: Text(
                step == 1 ? 'Insira o PIN atual' : 
                step == 2 ? 'Insira o novo PIN' : 'Confirme o novo PIN',
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    step == 1 ? 'Por favor, insira o seu PIN atual por segurança' :
                    step == 2 ? 'Insira o novo PIN para desativar o alarme.' : 'Confirme o novo PIN:',
                    style: const TextStyle(fontSize: 14),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: step == 1 ? currentPinController :
                               step == 2 ? newPinController : confirmPinController,
                    keyboardType: TextInputType.number,
                    obscureText: true,
                    maxLength: 7,
                    textAlign: TextAlign.center,
                    autofocus: true,
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                    decoration: InputDecoration(
                      filled: true,
                      fillColor: Colors.white,
                      hintText: 'PIN',
                      hintStyle: TextStyle(fontSize: 24, color: Colors.grey[400]),
                      border: InputBorder.none,
                      counterText: '',
                    ),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Cancelar'),
                ),
                TextButton(
                  onPressed: () async {
                    if (step == 1) {
                      if (currentPinController.text == _selectedPin) {
                        setStateDialog(() => step = 2);
                        currentPinController.clear();
                      } else {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('PIN atual errado'),
                            backgroundColor: Colors.red,
                          ),
                        );
                      }
                    } else if (step == 2) {
                      if (newPinController.text.length >= 4 &&
                          newPinController.text.length <= 7 &&
                          RegExp(r'^\d+$').hasMatch(newPinController.text)) {
                        setStateDialog(() => step = 3);
                      } else {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Por favor insira um PIN válido (4-7 digits)'),
                            backgroundColor: Colors.red,
                          ),
                        );
                      }
                    } else if (step == 3) {
                      if (confirmPinController.text == newPinController.text) {
                        setState(() => _selectedPin = newPinController.text);
                        await _savePin(_selectedPin);
                        if (context.mounted) Navigator.pop(context);
                        _showSaveConfirmation('PIN alterado com sucesso');
                      } else {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('PINs não são iguais'),
                            backgroundColor: Colors.red,
                          ),
                        );
                      }
                    }
                  },
                  child: Text(step == 3 ? 'Confirmar' : 'Próximo'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  /// Shows sound selection bottom sheet.
  void _showSoundOptions() {
    List<Map<String, dynamic>> soundOptions = [
      {'file': 'sound1.wav', 'label': 'Sound 1', 'isAsset': true},
      {'file': 'sound2.wav', 'label': 'Sound 2', 'isAsset': true},
      {'file': 'sound3.wav', 'label': 'Sound 3', 'isAsset': true},
    ];
    
    for (var imported in _importedSounds) {
      soundOptions.add({
        'file': imported['file'],
        'label': imported['label']?.replaceAll(RegExp(r'\.(mp3|wav|m4a)$'), '') ?? 'Imported Sound',
        'isAsset': false,
        'isImported': true,
        'fullPath': imported['file'],
      });
    }

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setStateBottomSheet) {
            return Container(
              height: MediaQuery.of(context).size.height * 0.7,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Padding(
                    padding: EdgeInsets.all(16),
                    child: Text('Escolha o Som', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  ),
                  const Divider(),
                  Expanded(
                    child: ListView(
                      children: [
                        ListTile(
                          leading: const Icon(Icons.folder, color: Color.fromARGB(255, 73, 69, 79)),
                          title: const Text('Importar áudio do dispositivo'),
                          subtitle: const Text('Selecionar o ficheiro', style: TextStyle(fontSize: 12)),
                          onTap: () async {
                            Navigator.pop(context);
                            await _importAudioFromDevice();
                            if (context.mounted) _showSoundOptions();
                          },
                        ),
                        ...soundOptions.map((sound) {
                          final isSelected = _selectedSound == sound['file'] ||
                              (_selectedSound == sound['fullPath']);
                          
                          return ListTile(
                            leading: IconButton(
                              icon: const Icon(Icons.play_arrow, color: Color.fromARGB(255, 73, 69, 79)),
                              onPressed: () => _playSoundPreview(
                                sound['file'], 
                                sound['isAsset'] as bool
                              ),
                              tooltip: 'Prévia do som',
                            ),
                            title: Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    sound['label'],
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                if (sound.containsKey('isImported') && sound['isImported'] == true)
                                  IconButton(
                                    icon: const Icon(Icons.delete_outline, color: Colors.red),
                                    onPressed: () async {
                                      Navigator.pop(context);
                                      final confirm = await showDialog<bool>(
                                        context: context,
                                        builder: (context) => AlertDialog(
                                          backgroundColor: const Color(0xFFE0F3FF),
                                          title: const Text('Remover áudio'),
                                          content: Text('Tem a certeza que quer eliminar "${sound['label']}"?'),
                                          actions: [
                                            TextButton(
                                              onPressed: () => Navigator.pop(context, false),
                                              child: const Text('Cancelar'),
                                            ),
                                            TextButton(
                                              onPressed: () => Navigator.pop(context, true),
                                              style: TextButton.styleFrom(foregroundColor: Colors.red),
                                              child: const Text('Remover'),
                                            ),
                                          ],
                                        ),
                                      );
                                      
                                      if (confirm == true) {
                                        await _deleteImportedSound(sound['file'], sound['label']);
                                      }
                                      
                                      if (context.mounted) _showSoundOptions();
                                    },
                                    tooltip: 'Remover som',
                                  ),
                              ],
                            ),
                            subtitle: Text(
                              sound['isAsset'] ? 'Som Padrão' : 'Importar áudio',
                              style: const TextStyle(fontSize: 12),
                            ),
                            trailing: isSelected ? const Icon(Icons.check, color: Colors.blue) : null,
                            onTap: () async {
                              _audioPlayer.stop();
                              setState(() {
                                _selectedSound = sound['isAsset'] ? sound['file'] : sound['file'];
                              });
                              await _saveSound(_selectedSound);
                              Navigator.pop(context);
                              _showSaveConfirmation('Som alterado para ${sound['label']}');
                            },
                          );
                        }).toList(),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    ).whenComplete(() => _audioPlayer.stop());
  }

  /// Shows a confirmation snackbar.
  void _showSaveConfirmation(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  /// Returns display name for selected sound.
  String _getSoundDisplayName() {
    String displayName;
    
    if (_selectedSound.startsWith('/')) {
      final fileName = path.basename(_selectedSound);
      displayName = fileName.replaceAll(RegExp(r'\.(mp3|wav|m4a)$'), '');
    } else {
      displayName = _selectedSound.replaceAll('.wav', '');
    }
    
    if (displayName.length > 15) {
      return '${displayName.substring(0, 15)}...';
    }
    
    return displayName;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 75.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSettingItem(
            icon: Icons.music_note,
            label: 'Som do Alarme',
            title: _getSoundDisplayName(),
            subtitle: 'Mudar o Som do Alarme',
            trailing: const Icon(Icons.arrow_drop_down, size: 30, color: Color(0xFF4A4A4A)),
            onTap: _showSoundOptions,
          ),
          const SizedBox(height: 40),
          _buildSettingItem(
            icon: Icons.lock_outline,
            label: 'PIN',
            title: _obscurePin ? '•' * _selectedPin.length : _selectedPin,
            subtitle: 'Mudar password',
            trailing: const Icon(Icons.arrow_drop_down, size: 30, color: Color(0xFF4A4A4A)),
            onTap: _showPinOptions,
          ),
        ],
      ),
    );
  }

  Widget _buildSettingItem({
    required IconData icon,
    required String label,
    required String title,
    required String subtitle,
    required Widget trailing,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            margin: const EdgeInsets.only(top: 20),
            child: Icon(icon, size: 28, color: const Color(0xFF4A4A4A)),
          ),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF4A4A4A)),
                ),
                const SizedBox(height: 4),
                Text(title, style: const TextStyle(fontSize: 20, color: Colors.black87)),
                const SizedBox(height: 2),
                Text(subtitle, style: TextStyle(fontSize: 14, color: Colors.grey[700])),
              ],
            ),
          ),
          Container(
            margin: const EdgeInsets.only(top: 20),
            child: trailing,
          ),
        ],
      ),
    );
  }
}
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const FlashcardApp());
}

class FlashcardApp extends StatelessWidget {
  const FlashcardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Flashcard Generator',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blueAccent),
        useMaterial3: true,
      ),
      home: const FlashcardHomePage(),
    );
  }
}

class FlashcardHomePage extends StatefulWidget {
  const FlashcardHomePage({super.key});

  @override
  State<FlashcardHomePage> createState() => _FlashcardHomePageState();
}

class _FlashcardHomePageState extends State<FlashcardHomePage> {
  final TextEditingController _promptController = TextEditingController();
  bool _isLoading = false;
  String? _error;
  List<Map<String, String>> _flashcards = [];

  Future<void> _generateFlashcards() async {
    final prompt = _promptController.text.trim();
    if (prompt.isEmpty) return;
    setState(() {
      _isLoading = true;
      _error = null;
      _flashcards = [];
    });
    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:5000/api/flashcards'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'prompt': prompt}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['flashcards'] is List) {
          final cardList = data['flashcards'] as List;
          _flashcards = cardList
              .map<Map<String, String>>(
                (f) => {
                  'question': f['question'].toString(),
                  'answer': f['answer'].toString(),
                },
              )
              .toList();
        } else {
          _error = 'Invalid response format.';
        }
      } else {
        _error = 'Backend error: ${response.statusCode}';
      }
    } catch (e) {
      _error = 'Failed to connect: $e';
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Flashcard Generator')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 500),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Enter a topic or prompt:',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _promptController,
                  decoration: const InputDecoration(
                    border: OutlineInputBorder(),
                    hintText: 'e.g. Photosynthesis, JavaScript basics...',
                  ),
                  onSubmitted: (_) => _generateFlashcards(),
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: _isLoading ? null : _generateFlashcards,
                  icon: const Icon(Icons.auto_awesome),
                  label: const Text('Generate Flashcards'),
                ),
                const SizedBox(height: 24),
                if (_isLoading) ...[
                  const Center(child: CircularProgressIndicator()),
                ] else if (_error != null) ...[
                  Text(_error!, style: const TextStyle(color: Colors.red)),
                ] else if (_flashcards.isNotEmpty) ...[
                  const Text(
                    'Generated Flashcards:',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Expanded(
                    child: ListView.separated(
                      itemCount: _flashcards.length,
                      itemBuilder: (context, idx) {
                        final card = _flashcards[idx];
                        return Card(
                          elevation: 3,
                          margin: EdgeInsets.zero,
                          child: ListTile(
                            title: Text(card['question'] ?? ''),
                            subtitle: Text(card['answer'] ?? ''),
                          ),
                        );
                      },
                      separatorBuilder: (context, idx) =>
                          const SizedBox(height: 10),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

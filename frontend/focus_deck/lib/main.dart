import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(const FocusDeckApp());
}

const backendBase = 'http://127.0.0.1:5000/api';
const tokenKey = 'fd_id_token';

class FocusDeckApp extends StatelessWidget {
  const FocusDeckApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FocusDeck',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blueAccent),
        useMaterial3: true,
      ),
      home: const MainScreen(),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String? _idToken;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadToken();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() => _idToken = prefs.getString(tokenKey));
  }

  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(tokenKey, token);
    setState(() => _idToken = token);
  }

  Future<void> _clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(tokenKey);
    setState(() => _idToken = null);
  }

  void _showSnack(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  Future<void> _showAuthDialog({required bool signup}) async {
    final emailCtrl = TextEditingController();
    final passCtrl = TextEditingController();
    final formKey = GlobalKey<FormState>();
    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(signup ? 'Signup' : 'Login'),
        content: Form(
          key: formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: emailCtrl,
                decoration: const InputDecoration(labelText: 'Email'),
                validator: (v) => v == null || v.isEmpty ? 'Required' : null,
              ),
              TextFormField(
                controller: passCtrl,
                decoration: const InputDecoration(labelText: 'Password'),
                obscureText: true,
                validator: (v) => v == null || v.length < 6 ? 'Min 6 chars' : null,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              if (!formKey.currentState!.validate()) return;
              Navigator.pop(ctx);
              if (signup) {
                await _authAPICall("signup", emailCtrl.text.trim(), passCtrl.text.trim());
                await _authAPICall("login", emailCtrl.text.trim(), passCtrl.text.trim());
              } else {
                await _authAPICall("login", emailCtrl.text.trim(), passCtrl.text.trim());
              }
            },
            child: Text(signup ? 'Signup' : 'Login'),
          ),
        ],
      ),
    );
  }

  Future<void> _authAPICall(String type, String email, String pass) async {
    try {
      final resp = await http.post(
        Uri.parse('$backendBase/$type'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': pass}),
      );
      if (type == 'login' && resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        await _saveToken(data['idToken']);
        _showSnack("Logged in!");
      } else if (type == 'signup' && resp.statusCode == 200) {
        _showSnack("Signup success! Please login.");
      } else {
        _showSnack("Auth failed");
      }
    } catch (_) {
      _showSnack("Auth error");
    }
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("FocusDeck"),
        actions: [
          if (_idToken == null)
            Row(children: [
              TextButton(onPressed: () => _showAuthDialog(signup: false), child: const Text("Login")),
              TextButton(onPressed: () => _showAuthDialog(signup: true), child: const Text("Signup")),
            ])
          else
            TextButton(
              onPressed: () async { await _clearToken(); _showSnack("Logged out"); setState(() {}); },
              child: const Text("Logout"),
            ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [Tab(text: 'Flashcards'), Tab(text: 'Study Guides')],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          FlashcardTab(idToken: _idToken, snack: _showSnack),
          StudyGuideTab(idToken: _idToken, snack: _showSnack),
        ],
      ),
    );
  }
}

class FlashcardTab extends StatefulWidget {
  final String? idToken;
  final void Function(String) snack;
  const FlashcardTab({super.key, required this.idToken, required this.snack});

  @override
  State<FlashcardTab> createState() => _FlashcardTabState();
}

class _FlashcardTabState extends State<FlashcardTab> {
  final TextEditingController _promptController = TextEditingController();
  List<Map<String, String>> _flashcards = [];
  bool _isLoading = false;
  String? _error;

  Future<void> _generateFlashcards() async {
    final prompt = _promptController.text.trim();
    if (prompt.isEmpty) return;
    setState(() {
      _isLoading = true;
      _error = null;
      _flashcards = [];
    });
    try {
      final resp = await http.post(
        Uri.parse('$backendBase/generate_flashcards'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'notes': prompt}),
      );
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        final flashcardsData = data['flashcards'] as List? ?? [];
        _flashcards = flashcardsData.map((c) {
          if (c is Map<String, dynamic>) {
            return {
              'question': c['question']?.toString() ?? '',
              'answer': c['answer']?.toString() ?? ''
            };
          } else if (c is Map) {
            // fallback for any Map type
            return Map<String, String>.fromEntries(
              c.entries.map((e) => MapEntry(e.key.toString(), e.value?.toString() ?? '')),
            );
          } else {
            return {'question': '', 'answer': ''};
          }
        }).toList();
      } else {
        _error = 'Failed to generate.';
      }
    } catch (e) {
      _error = e.toString();
    }
    setState(() => _isLoading = false);
  }

  Future<void> _saveFlashcardSet() async {
    if (widget.idToken == null) return widget.snack("Login first");
    if (_flashcards.isEmpty) return;
    final titleCtrl = TextEditingController();
    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text("Save Flashcard Set"),
        content: TextField(
          controller: titleCtrl,
          decoration: const InputDecoration(labelText: "Title"),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Cancel")),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              setState(() => _isLoading = true);
              await http.post(
                Uri.parse('$backendBase/flashcards/save'),
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': widget.idToken!,
                },
                body: jsonEncode({
                  'set_title': titleCtrl.text.trim(),
                  'flashcards': _flashcards,
                }),
              );
              setState(() => _isLoading = false);
              widget.snack("Saved!");
            },
            child: const Text("Save"),
          ),
        ],
      ),
    );
  }

  Future<void> _loadSavedFlashcards() async {
    if (widget.idToken == null) return widget.snack("Login first");
    setState(() => _isLoading = true);
    try {
      final resp = await http.get(
        Uri.parse('$backendBase/flashcards/load'),
        headers: {'Authorization': widget.idToken!},
      );
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        _showFlashcardSetsDialog(data['sets'] ?? []);
      } else {
        widget.snack("Failed to load");
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showFlashcardSetsDialog(List sets) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text("Saved Flashcard Sets"),
        content: SizedBox(
          width: 400,
          height: 400,
          child: ListView.builder(
            itemCount: sets.length,
            itemBuilder: (ctx, i) {
              final s = sets[i];
              return ListTile(
                title: Text(s['title']),
                onTap: () {
                  Navigator.pop(ctx);
                  Future.delayed(Duration.zero, () {
                    if (!mounted) return;
                    _showFlashcardSetDialog(s, context);
                  });
                },
                trailing: IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () async {
                    await http.delete(
                      Uri.parse('$backendBase/flashcards/delete/${s['id']}'),
                      headers: {'Authorization': widget.idToken!},
                    );
                    Navigator.pop(ctx);
                    if (!mounted) return;
                    _loadSavedFlashcards();
                    widget.snack("Flashcard set deleted!");
                  },
                ),
              );
            },
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Close")),
        ],
      ),
    );
  }

  void _showFlashcardSetDialog(Map set, BuildContext dialogCtx) {
    showDialog(
      context: dialogCtx,
      builder: (ctx) => AlertDialog(
        title: Text(set['title']),
        content: SizedBox(
          width: 400,
          height: 400,
          child: ListView.builder(
            itemCount: set['cards'].length,
            itemBuilder: (ctx, i) {
              final c = set['cards'][i];
              return Card(
                child: ListTile(
                  title: Text(c['question']),
                  subtitle: Text(c['answer']),
                ),
              );
            },
          ),
        ),
        actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Close'))],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(children: [
        TextField(
          controller: _promptController,
          decoration: const InputDecoration(
            labelText: "Enter notes or topic",
            border: OutlineInputBorder(),
          ),
          maxLines: 4,
        ),
        const SizedBox(height: 12),
        Row(children: [
          ElevatedButton(
            onPressed: _isLoading ? null : _generateFlashcards,
            child: const Text("Generate Flashcards"),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            onPressed: _flashcards.isEmpty ? null : _saveFlashcardSet,
            child: const Text("Save Set"),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            onPressed: _loadSavedFlashcards,
            child: const Text("Load Saved"),
          ),
        ]),
        const SizedBox(height: 16),
        if (_isLoading) const CircularProgressIndicator(),
        if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
        const SizedBox(height: 12),
        Expanded(
          child: ListView.builder(
            itemCount: _flashcards.length,
            itemBuilder: (ctx, i) {
              final c = _flashcards[i];
              return Card(
                child: ListTile(
                  title: Text(c['question'] ?? ''),
                  subtitle: Text(c['answer'] ?? ''),
                ),
              );
            },
          ),
        ),
      ]),
    );
  }
}

class StudyGuideTab extends StatefulWidget {
  final String? idToken;
  final void Function(String) snack;
  const StudyGuideTab({super.key, required this.idToken, required this.snack});
  @override
  State<StudyGuideTab> createState() => _StudyGuideTabState();
}

class _StudyGuideTabState extends State<StudyGuideTab> {
  final TextEditingController _promptController = TextEditingController();
  String _studyGuide = "";
  List<Map<String, dynamic>> _guides = [];
  bool _isLoading = false;
  String? _error;

  Future<void> _generateStudyGuide() async {
    final prompt = _promptController.text.trim();
    if (prompt.isEmpty) return;
    setState(() {
      _isLoading = true;
      _error = null;
      _studyGuide = "";
    });
    try {
      final resp = await http.post(
        Uri.parse('$backendBase/generate_study_guide'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'notes': prompt}),
      );
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        setState(() { _studyGuide = data['guide'] ?? ""; });
      } else {
        _error = 'Failed to generate.';
      }
    } catch (e) {
      _error = e.toString();
    }
    setState(() => _isLoading = false);
  }

  Future<void> _saveStudyGuide() async {
    if (widget.idToken == null) return widget.snack("Login first");
    if (_studyGuide.isEmpty) return;
    final titleCtrl = TextEditingController();
    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text("Save Study Guide"),
        content: TextField(
          controller: titleCtrl,
          decoration: const InputDecoration(labelText: "Title"),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Cancel")),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              setState(() => _isLoading = true);
              await http.post(
                Uri.parse('$backendBase/study_guides/save'),
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': widget.idToken!,
                },
                body: jsonEncode({
                  'title': titleCtrl.text.trim(),
                  'content': _studyGuide,
                }),
              );
              setState(() => _isLoading = false);
              widget.snack("Saved!");
            },
            child: const Text("Save"),
          ),
        ],
      ),
    );
  }

  Future<void> _loadStudyGuides() async {
    if (widget.idToken == null) return widget.snack("Login first");
    setState(() => _isLoading = true);
    try {
      final resp = await http.get(
        Uri.parse('$backendBase/study_guides/load'),
        headers: {'Authorization': widget.idToken!},
      );
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        setState(() { _guides = List<Map<String, dynamic>>.from(data['guides'] ?? []); });
        _showGuidesDialog();
      } else {
        widget.snack("Failed to load");
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showGuidesDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text("Saved Study Guides"),
        content: SizedBox(
          width: 400,
          height: 400,
          child: ListView.builder(
            itemCount: _guides.length,
            itemBuilder: (ctx, i) {
              final g = _guides[i];
              return ListTile(
                title: Text(g['title'] ?? 'Untitled Guide'),
                onTap: () {
                  Navigator.pop(ctx);
                  Future.delayed(Duration.zero, () {
                    if (!mounted) return;
                    _showGuideDetailDialog(g, context);
                  });
                },
                trailing: IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () async {
                    await http.delete(
                      Uri.parse('$backendBase/study_guides/delete/${g['id']}'),
                      headers: {'Authorization': widget.idToken!},
                    );
                    Navigator.pop(ctx);
                    if (!mounted) return;
                    _loadStudyGuides();
                    widget.snack("Study guide deleted!");
                  },
                ),
              );
            },
          ),
        ),
        actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Close"))],
      ),
    );
  }
  void _showGuideDetailDialog(Map guide, BuildContext dialogCtx) {
    showDialog(
      context: dialogCtx,
      builder: (ctx) => AlertDialog(
        title: Text(guide['title'] ?? 'Untitled Guide'),
        content: SingleChildScrollView(child: Text(guide['content'] ?? '')),
        actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Close'))],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(children: [
        TextField(
          controller: _promptController,
          decoration: const InputDecoration(
            labelText: "Enter notes or topic for Study Guide",
            border: OutlineInputBorder(),
          ),
          maxLines: 4,
        ),
        const SizedBox(height: 12),
        Row(children: [
          ElevatedButton(
            onPressed: _isLoading ? null : _generateStudyGuide,
            child: const Text("Generate Guide"),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            onPressed: _studyGuide.isEmpty ? null : _saveStudyGuide,
            child: const Text("Save Guide"),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            onPressed: _loadStudyGuides,
            child: const Text("Load Saved"),
          ),
        ]),
        const SizedBox(height: 16),
        if (_isLoading) const CircularProgressIndicator(),
        if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
        const SizedBox(height: 12),
        if (_studyGuide.isNotEmpty) Expanded(
          child: SingleChildScrollView(child: Text(_studyGuide)),
        ),
      ]),
    );
  }
}


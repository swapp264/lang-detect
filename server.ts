import express from 'express';
import { createServer as createViteServer } from 'vite';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

async function startServer() {
  const app = express();
  const PORT = parseInt(process.env.PORT || '3000', 10);

  app.use(express.json({ limit: '10mb' }));

  // Helper to execute Python predict CLI
  const executePythonPredict = (text: string, topK: number = 3): Promise<any> => {
    return new Promise((resolve, reject) => {
      const payload = JSON.stringify({ text, top_k: topK });
      const py = spawn('python3', ['-m', 'src.predict', '--json', payload], {
        cwd: process.cwd(),
      });

      let stdout = '';
      let stderr = '';

      py.stdout.on('data', (chunk) => {
        stdout += chunk.toString();
      });

      py.stderr.on('data', (chunk) => {
        stderr += chunk.toString();
      });

      py.on('close', (code) => {
        if (code !== 0) {
          try {
            const errObj = JSON.parse(stdout);
            return reject(new Error(errObj.error || stderr || `Python exited with code ${code}`));
          } catch {
            return reject(new Error(stderr.trim() || stdout.trim() || `Execution failed with code ${code}`));
          }
        }

        try {
          // Parse JSON, ignoring any potential runtime warning lines before valid JSON
          const jsonStart = stdout.indexOf('{');
          if (jsonStart === -1) {
            return reject(new Error('Invalid response from prediction engine.'));
          }
          const parsed = JSON.parse(stdout.slice(jsonStart));
          resolve(parsed);
        } catch (err: any) {
          reject(new Error(`Failed to parse model output: ${err.message}`));
        }
      });
    });
  };

  // Prediction endpoint: supports both /predict and /api/predict
  const handlePredict = async (req: express.Request, res: express.Response) => {
    try {
      const text = req.body?.text;
      const topK = req.body?.top_k || 3;

      if (!text || typeof text !== 'string' || !text.trim()) {
        return res.status(400).json({ error: 'Text cannot be empty or whitespace only.' });
      }

      if (text.trim().length < 2) {
        return res.status(400).json({
          error: 'Input text is too short. Please provide at least 2 characters for reliable classification.',
        });
      }

      const result = await executePythonPredict(text, topK);
      return res.json(result);
    } catch (error: any) {
      console.error('Prediction error:', error);
      return res.status(400).json({ error: error.message || 'Classification failed.' });
    }
  };

  app.post('/predict', handlePredict);
  app.post('/api/predict', handlePredict);

  // Health endpoint
  const handleHealth = (req: express.Request, res: express.Response) => {
    const modelPath = path.join(process.cwd(), 'models', 'language_detector.pkl');
    const modelExists = fs.existsSync(modelPath);

    res.json({
      status: 'healthy',
      model_loaded: modelExists,
      supported_languages_count: 15,
      version: '1.0.0',
      runtime: 'FastAPI / Python ML + Express SSR Proxy',
    });
  };

  app.get('/health', handleHealth);
  app.get('/api/health', handleHealth);

  // Supported languages endpoint
  const handleLanguages = (req: express.Request, res: express.Response) => {
    const metadataPath = path.join(process.cwd(), 'models', 'model_metadata.json');
    if (fs.existsSync(metadataPath)) {
      try {
        const meta = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));
        const languages = Object.entries(meta.languages_info || {}).map(([name, info]: [string, any]) => ({
          name,
          ...info,
        }));
        return res.json({ count: languages.length, languages });
      } catch (e) {
        // Fallback below
      }
    }

    const fallback = [
      { name: 'English', flag: '🇬🇧', code: 'en', script: 'Latin', native: 'English' },
      { name: 'Hindi', flag: '🇮🇳', code: 'hi', script: 'Devanagari', native: 'हिन्दी' },
      { name: 'Marathi', flag: '🇮🇳', code: 'mr', script: 'Devanagari', native: 'मराठी' },
      { name: 'French', flag: '🇫🇷', code: 'fr', script: 'Latin', native: 'Français' },
      { name: 'German', flag: '🇩🇪', code: 'de', script: 'Latin', native: 'Deutsch' },
      { name: 'Spanish', flag: '🇪🇸', code: 'es', script: 'Latin', native: 'Español' },
      { name: 'Italian', flag: '🇮🇹', code: 'it', script: 'Latin', native: 'Italiano' },
      { name: 'Portuguese', flag: '🇵🇹', code: 'pt', script: 'Latin', native: 'Português' },
      { name: 'Russian', flag: '🇷🇺', code: 'ru', script: 'Cyrillic', native: 'Русский' },
      { name: 'Arabic', flag: '🇸🇦', code: 'ar', script: 'Arabic', native: 'العربية' },
      { name: 'Chinese', flag: '🇨🇳', code: 'zh', script: 'Hanzi', native: '中文' },
      { name: 'Japanese', flag: '🇯🇵', code: 'ja', script: 'Kanji+Kana', native: '日本語' },
      { name: 'Korean', flag: '🇰🇷', code: 'ko', script: 'Hangul', native: '한국어' },
      { name: 'Dutch', flag: '🇳🇱', code: 'nl', script: 'Latin', native: 'Nederlands' },
      { name: 'Turkish', flag: '🇹🇷', code: 'tr', script: 'Latin (Ext)', native: 'Türkçe' },
    ];
    res.json({ count: fallback.length, languages: fallback });
  };

  app.get('/languages', handleLanguages);
  app.get('/api/languages', handleLanguages);

  // Metrics endpoint
  const handleMetrics = (req: express.Request, res: express.Response) => {
    const metadataPath = path.join(process.cwd(), 'models', 'model_metadata.json');
    if (fs.existsSync(metadataPath)) {
      try {
        const meta = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));
        return res.json(meta);
      } catch (e: any) {
        return res.status(500).json({ error: 'Failed to read metadata file' });
      }
    }
    res.status(404).json({ error: 'Model metadata not found. Train model first.' });
  };

  app.get('/metrics', handleMetrics);
  app.get('/api/metrics', handleMetrics);

  // Mount Vite middleware for dev
  const vite = await createViteServer({
    server: { middlewareMode: true },
    appType: 'spa',
  });
  app.use(vite.middlewares);

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Language Detection System Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer().catch((err) => {
  console.error('Failed to start server:', err);
  process.exit(1);
});

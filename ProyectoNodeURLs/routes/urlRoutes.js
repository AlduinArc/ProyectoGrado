const express = require('express');
const router = express.Router();
const { saveUrl, findUrl } = require('../storage');

// Página principal (formulario)
router.get('/', (req, res) => {
  res.render('index');
});

// Acortar URL
router.post('/shorten', (req, res) => {
  const { fullUrl } = req.body;
  const url = saveUrl(fullUrl);
  res.render('result', { shortUrl: url.shortUrl });
});

// Redirigir al enlace original
router.get('/:shortUrl', (req, res) => {
  const url = findUrl(req.params.shortUrl);
  if (!url) return res.status(404).send('URL no encontrada');
  res.redirect(url.fullUrl);
});

module.exports = router;
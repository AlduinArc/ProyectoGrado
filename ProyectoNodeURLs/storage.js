const shortId = require('shortid');

let urls = []; // Array en memoria (simula una DB)

// Funci�n para guardar una URL
const saveUrl = (fullUrl) => {
  const existingUrl = urls.find((url) => url.fullUrl === fullUrl);
  if (existingUrl) return existingUrl; // Si ya existe, retornarla

  const newUrl = {
    fullUrl,
    shortUrl: shortId.generate(),
    clicks: 0,
  };
  urls.push(newUrl);
  return newUrl;
};

// Funci�n para buscar una URL corta
const findUrl = (shortUrl) => {
  const url = urls.find((url) => url.shortUrl === shortUrl);
  if (!url) return null;

  url.clicks++; // Incrementar clicks al acceder
  return url;
};

module.exports = { saveUrl, findUrl };
// Polyfill for Blob in Node.js environments that don't have it
if (typeof global.Blob === 'undefined') {
  const { Blob } = require('buffer');
  global.Blob = Blob;
} 
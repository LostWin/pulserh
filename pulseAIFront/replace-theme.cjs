const fs = require('fs');
const path = require('path');

const replacements = {
  // Backgrounds
  'bg-slate-50': 'bg-brand-light',
  'bg-slate-100': 'bg-brand-light',
  'bg-slate-800': 'bg-brand-dark',
  'bg-slate-900': 'bg-brand-dark',
  'bg-indigo-50': 'bg-brand-light',
  'bg-indigo-100': 'bg-brand-light',
  'bg-indigo-500': 'bg-brand-secondary',
  'bg-indigo-600': 'bg-brand-secondary',
  'bg-blue-50': 'bg-brand-light',
  'bg-blue-600': 'bg-brand-secondary',
  'bg-blue-500': 'bg-brand-secondary',
  'bg-red-50': 'bg-brand-danger/10',
  'bg-red-100': 'bg-brand-danger/20',
  'bg-red-500': 'bg-brand-danger',
  'bg-red-600': 'bg-brand-danger',
  'bg-emerald-50': 'bg-brand-light',
  'bg-emerald-100': 'bg-brand-secondary/20',
  'bg-emerald-500': 'bg-brand-secondary',
  'bg-emerald-600': 'bg-brand-secondary',
  
  // Texts
  'text-slate-400': 'text-brand-secondary/70',
  'text-slate-500': 'text-brand-secondary/80',
  'text-slate-600': 'text-brand-secondary',
  'text-slate-700': 'text-brand-dark',
  'text-slate-800': 'text-brand-dark',
  'text-slate-900': 'text-brand-dark',
  'text-indigo-600': 'text-brand-secondary',
  'text-indigo-500': 'text-brand-secondary',
  'text-blue-600': 'text-brand-secondary',
  'text-blue-500': 'text-brand-secondary',
  'text-red-600': 'text-brand-danger',
  'text-red-500': 'text-brand-danger',
  'text-emerald-600': 'text-brand-secondary',
  'text-emerald-500': 'text-brand-secondary',
  
  // Borders
  'border-slate-100': 'border-brand-secondary/10',
  'border-slate-200': 'border-brand-secondary/20',
  'border-slate-300': 'border-brand-secondary/30',
  'border-slate-800': 'border-white/10',
  'border-indigo-100': 'border-brand-secondary/20',
  'border-indigo-200': 'border-brand-secondary/30',
  'border-blue-100': 'border-brand-secondary/20',
  
  // Rings
  'ring-slate-500/20': 'ring-brand-secondary/20',
  'ring-indigo-600': 'ring-brand-secondary',
  'ring-blue-500': 'ring-brand-secondary',

  // Rounding
  'rounded-2xl': 'rounded-xl',
  'rounded-lg': 'rounded-xl',
  'rounded-md': 'rounded-xl',
};

function processDirectory(dirPath) {
  const files = fs.readdirSync(dirPath);
  for (const file of files) {
    const fullPath = path.join(dirPath, file);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      processDirectory(fullPath);
    } else if (fullPath.endsWith('.jsx')) {
      processFile(fullPath);
    }
  }
}

function processFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let originalContent = content;
  
  for (const [key, value] of Object.entries(replacements)) {
    const regex = new RegExp('\\b' + key.replace(/\//g, '\\/') + '\\b', 'g');
    content = content.replace(regex, value);
  }
  
  if (content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log('Updated', filePath);
  }
}

processDirectory('c:\\Users\\graci\\Downloads\\front-lahou\\src');
console.log('Done.');

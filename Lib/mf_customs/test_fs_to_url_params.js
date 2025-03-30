const fs = require('fs');
const path = require('path');

const filePath = path.resolve('./Lib/mf_customs/test_fs.py');
const fileContent = fs.readFileSync(filePath, 'utf8');
console.log(encodeURIComponent(fileContent))

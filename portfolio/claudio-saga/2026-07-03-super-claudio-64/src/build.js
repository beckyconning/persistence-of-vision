const fs = require('fs');
const three = fs.readFileSync('three.min.js', 'utf8');
const srcs = fs.readdirSync('src').sort().map(f => fs.readFileSync('src/' + f, 'utf8')).join('\n');
let shell = fs.readFileSync('shell.html', 'utf8');
shell = shell.replace('<!-- THREE_JS_HERE -->', '<script>\n' + three + '\n</script>');
shell = shell.replace('<!-- GAME_JS_HERE -->', '<script>\n' + srcs + '\n</script>');
fs.writeFileSync('claudio64.html', shell);
console.log('built claudio64.html', (shell.length / 1024).toFixed(0) + 'KB');

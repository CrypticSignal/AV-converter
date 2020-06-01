let previousLine = ''
async function read_progress() {
    while (true) {
        const response = await fetch('static/output.txt');
        const textInFile = await response.text();
        lines = textInFile.split('\n');
        secondLastLine = lines[lines.length - 2];
        if (typeof secondLastLine === 'undefined') {
            secondLastLine = ':)';
        }
        if (secondLastLine.includes('Deleting')) {
            secondLastLine = '';
        }
        document.getElementById('progress').innerHTML = secondLastLine;
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
}
// function read_progress() {
//     fetch ('static/output.txt')
//     .then(function(res) {
//         return res.text()
//     })
//     .then(function(data){
//         document.getElementById('progress').innerHTML = data;
//     })
// }
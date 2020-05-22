function wait(ms){
   var start = new Date().getTime();
   var end = start;
   while(end < start + ms) {
     end = new Date().getTime();
  }
}

function resize(){
    top.resizeTo(900, 500);
}

window.onresize = function(event) {
    resize();
};


async function checkUpdates() {
    eel.checkUpdates_py()
}

if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.write('<link id="style" rel="stylesheet" type="text/css" href="/style-dark.css"/>');
} else {
    document.write('<link id="style" rel="stylesheet" type="text/css" href="/style.css" title="light"/>');
}

function mode() {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.getElementById('style').href = "style-dark.css";
    } else {
        document.getElementById('style').href = "style.css";
    }
}
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    mode();
})

function showExtract(){
    document.getElementById('main').style = "top:100%;";
    //wait(100);
    document.getElementById('extract').style = "top:0%;";
}
function showMenu(){
    document.getElementById('extract').style = "top:100%;;";
    document.getElementById('create').style = "top:100%;";
    //wait(100);
    document.getElementById('main').style = "top:0%;";
}
function showCreate(){
    document.getElementById('main').style = "top:100%;";
    //wait(100);
    document.getElementById('create').style = "top:0%;";
}

async function openFile() {
    let result = await eel.openFile()();
    if (!(result == 0)){
        document.getElementById('filesToZip').value = document.getElementById('filesToZip').value + '◼' + result + '\n';
    }
}

eel.expose(showFileError); // Expose this function to Python
      function showFileError(x) {
        alert('Unable to add file "' + x + '" to ZIP file. The file will be skipped');
      }
eel.expose(showAlert); // Expose this function to Python
      function showAlert(x) {
        alert(x);
      }

function removeFile(){
    console.log('remove file')
}
async function openZip() {
    let result = await eel.openZIP()();
    if (!(result == 0)){
        document.getElementById('zipToFiles').value = '◼' + result + '\n';
    }
}

async function createZip() {
    let result = await eel.createZip()();
    if(result==1){
        alert('ZIP Creation Done');
        document.getElementById('filesToZip').value = '';
    }
    else{
        alert('Error Occurred')
    }
}
async function extractZip() {
    let result = await eel.extractZip()();
    if(result==1){
        alert('ZIP Extraction Done');
        document.getElementById('zipToFiles').value = '';
    }
    else{
        alert('Error Occurred')
    }
}
function wait(ms) {
    var start = new Date().getTime();
    var end = start;
    while (end < start + ms) {
        end = new Date().getTime();
    }
}

async function checkUpdates() {
    eel.checkUpdates_py()
}

if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.write('<link id="style" rel="stylesheet" type="text/css" href="/style-dark.css"/>');
} else {
    document.write('<link id="style" rel="stylesheet" type="text/css" href="/style.css" title="light"/>');
}
window.onresize = function(event) {
    document.getElementById('filesToZip').style.width = window.innerWidth-450;
    document.getElementById('progressBar').style.width = window.innerWidth-40;
    document.getElementById('zipToFiles').style.width = window.innerWidth-450;
    document.getElementById('extractProgressBar').style.width = window.innerWidth-40;
};

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
eel.expose(showExtract);

function showExtract() {
    document.getElementById('main').style = "top:100%;";
    //wait(100);
    document.getElementById('extractProgressBarPiece').style.width = "00%";
    document.getElementById('extract').style = "top:0%;";
}

function showMenu() {
    document.getElementById('extract').style = "top:100%;;";
    document.getElementById('create').style = "top:100%;";
    //wait(100);
    document.getElementById('main').style = "top:0%;";
}

function showCreate() {
    document.getElementById('main').style = "top:100%;";
    //wait(100);
    document.getElementById('create').style = "top:0%;";
}

async function openFile() {
    let result = await eel.openFile()();
    if (!(result == 0)) {
        document.getElementById('filesToZip').value = document.getElementById('filesToZip').value + '◼' + result + '\n';
    }
}

async function openFolder() {
    let result = await eel.openFolder()();
    if (!(result == 0)) {
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

eel.expose(progressbar);

function progressbar(p) {
    if (p >= 99.5) {
        p = 100;
    }
    console.log(p);
    document.getElementById('progressBarPiece').style.width = p + '%';
}

function clearFiles() {
    eel.clearZipFiles()();
    document.getElementById('filesToZip').value = '';
}

eel.expose(yellowProgressbar);

function yellowProgressbar() {
    document.getElementById('progressBarPiece').style = "background-color:rgba(255,255,0,0.5);";
}

eel.expose(completeProgressbar);

function completeProgressbar() {
    document.getElementById('progressBarPiece').style.width = "100%";
}

eel.expose(nextStepExtractProgressBar)

function nextStepExtractProgressBar() {
    document.getElementById('extractProgressBarPiece').style.width = "100%";
}

eel.expose(resetExtractProgressBar)

function resetExtractProgressBar() {
    document.getElementById('extractProgressBarPiece').style.width = "00%";
}

async function openZip() {
    let result = await eel.openZIP()();
    if (!(result == 0)) {
        document.getElementById('zipToFiles').value = '◼' + result + '\n';
    }
}

async function createZip() {
    let result = await eel.createZip()();
    if (result == 1) {
        document.getElementById('filesToZip').value = '';
        document.getElementById('progressBarPiece').style = 'width: 0%;';
    } else {
        document.getElementById('progressBarPiece').style = 'width: 0%;';
    }
    document.getElementById('progressBarPiece').style = 'background-color: rgba(51,255,51,0.5);'
}
async function extractZip() {
    let result = await eel.extractZip()();
    if (result == 1) {
        document.getElementById('zipToFiles').value = '';
        document.getElementById('extractProgressBarPiece').style.width = '0%';
    } else {
        document.getElementById('extractProgressBarPiece').style.width = '0%';
    }
}

eel.extractFirstZip()();

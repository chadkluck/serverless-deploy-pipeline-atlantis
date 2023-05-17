
const JSZip = require("jszip");
const fs = require("fs");
const path = require('path');

/**
 * 
 * @param {JSZip} zip 
 * @param {string} directoryPath 
 * @param {string} zipPath 
 * @returns {JSZip}
 */
const zipFolder = function (zip, directoryPath, zipPath = "") {
	fs.readdir(directoryPath, function (err, files) {
		//handling error
		if (err) {
			return console.log('Unable to scan directory: ' + err);
		}

		//listing all files using forEach
		files.forEach(function (file) {
			// check if file is directory
			if (fs.lstatSync(path.join(directoryPath, file)).isDirectory()) {
				zip.folder(path.join(zipPath, file));
				zip = zipFolder(zip, path.join(directoryPath, file), path.join(zipPath, file));
			} else if (fs.lstatSync(path.join(directoryPath, file)).isFile()) {
				let src = path.join(directoryPath, file);
				let dest = path.join(zipPath, file);
				zip.file(dest, fs.readFileSync(src));
				console.log(`FILE ${src} ADDED AS ${dest} TO ZIP`);
			} else {
				console.log(`FILE ${path.join(directoryPath, file)} IS NOT A FILE OR DIRECTORY. SKIPPING.`);
			}
		});
	});

	return zip;
}
let zip = new JSZip();
const directoryPath = path.join('..', 'codecommit-example-lambda-infrastructure');
zip = zipFolder(zip, directoryPath);

zip
.generateNodeStream({type:'nodebuffer',streamFiles:true})
.pipe(fs.createWriteStream('build/infrastructure.zip'), { end: true})
.on('finish', function () {
    // JSZip generates a readable stream with a "end" event,
    // but is piped here in a writable stream which emits a "finish" event.
    console.log("build/infrastructure.zip written.");
})
.on('error', function (e) {
    console.error();(e);
    throw e;
});
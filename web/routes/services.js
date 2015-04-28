var PythonShell = require('python-shell');


module.exports = function (app) {

    app.post('/sickBeetz', function(req,res){
        console.log(req.files);
        var inp =req.files.audio.path;
        PythonShell.run('sickBeetz.py', {args: [inp,'kit_1'], scriptPath:'../', pythonOptions: ['-W ignore']}, function(err, results){
            console.log(results);
            res.download(inp.substring(0, inp.length - 4) + '-out.wav')
        });
    });
};

var PythonShell = require('python-shell');


module.exports = function (app) {

    app.post('/sickBeetz', function(req,res){
        console.log(req.files);
        var kit= req.body.kit;
        var inp =req.files.file.path;
        PythonShell.run('sickBeetz.py', {args: [inp, kit], scriptPath:'../', pythonOptions: ['-W ignore']}, function(err, results){
            console.log(results);
            var filename = inp.substring(0, inp.length - 4) + '-out.wav';
            res.send({
                path:filename
            })
        });
    });
};

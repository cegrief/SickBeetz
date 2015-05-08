var express = require('express');
var multer = require('multer');
var http = require('http');
var path = require('path');
var bodyParser = require('body-parser');

var app = express();

app.set('port', 5000);


app.use(express.static(path.join(__dirname, '/views/')));
app.use('/bower_components', express.static(__dirname + '/bower_components'));
app.use('/uploads', express.static(__dirname + '/uploads'));

app.use(bodyParser.json());

app.use(multer({
  dest:'./uploads/',
  onFileUploadStart:function(file,req,res){
    file.extension = '.wav'
  },
  rename:function(fieldname,filename,req,res){
    return 'sickBeetz-'+filename+Date.now();
  }}));

require('./routes/services')(app);

http.createServer(app).listen(app.get('port'), function () {
  console.log('Express server listening on port ' + app.get('port'));
});
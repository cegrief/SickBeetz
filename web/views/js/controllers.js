angular.module('secrets.controllers', [])
    .controller('indexController', function($scope, $http){
        var navigator = window.navigator;
        navigator.getUserMedia = (navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia);
        var Context = window.AudioContext || window.webkitAudioContext;
        var context = new Context();

        var mediaStream;
        var rec;

        $scope.kit='kit_2';

        $scope.submitForm=function(){
            var file = $scope.input;
            var fd = new FormData();
            fd.append('file', file);
            fd.append('kit', $scope.kit);
            $http.post('/sickBeetz',fd,{
                transformReques: angular.identity,
                headers: {'Content-Type':undefined}
            }).then(function(res){
                console.log(res);
                $scope.audiopath = res.data.path;
            });
        };

        $scope.record = function() {
            $scope.recorded =false;
            // ask for permission and start recording
            navigator.getUserMedia({audio: true}, function(localMediaStream){
                mediaStream = localMediaStream;

                // create a stream source to pass to Recorder.js
                var mediaStreamSource = context.createMediaStreamSource(localMediaStream);

                // create new instance of Recorder.js using the mediaStreamSource
                rec = new Recorder(mediaStreamSource, {
                    // pass the path to recorderWorker.js file here
                    workerPath: '/bower_components/recorderjs/recorderWorker.js'
                });

                // start recording
                rec.record();
            }, function(err){
                console.log('Browser not supported');
            });
        }

        $scope.stop = function() {
            // stop the media stream
            mediaStream.stop();
            // stop Recorder.js
            rec.stop();

            // export it to WAV
            rec.exportWAV(function(e){
                //clear the current recording so subsequent calls don't just add onto it
                rec.clear();
                console.log(e);
                $scope.input = blobToFile(e, 'input.wav');
                $scope.recorded = true;
                $scope.$apply();
            });
        };

        function blobToFile(theBlob, fileName){
            //A Blob() is almost a File() - it's just missing the two properties below which we will add
            theBlob.lastModifiedDate = new Date();
            theBlob.name = fileName;
            return theBlob;
        }

    });
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
            $scope.audiopath = undefined;
            $scope.submitted = true;
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
                $scope.recording = true;
                $scope.alerts.push({type: 'info', msg: 'Recording...'});
                $scope.$apply();
                rec.record();
            }, function(err){
                console.log('Browser not supported');
            });
        };

        $scope.stop = function() {
            $scope.recording = false;

            $scope.alerts.splice(0);
            $scope.alerts.push({type: 'success', msg: 'Audio Recorded Successfully! Play it back to review, or select a Kit and Submit it to SickBeetz'});

            // stop the media stream
            mediaStream.stop();
            // stop Recorder.js
            rec.stop();

            // export it to WAV
            rec.exportWAV(function(e){
                //clear the current recording so subsequent calls don't just add onto it
                rec.clear();


                //create an object URL for playback
                var url = URL.createObjectURL(e);
                $scope.playaudio = new Audio();
                $scope.playaudio.src = url;

                //add some file metadata for sending to the server;
                $scope.input = blobToFile(e, 'input.wav');
                $scope.recorded = true;
                $scope.$apply();
            });
        };

        $scope.play = function(){
            $scope.playaudio.play();
        };

        $scope.stopaudio = function(){
            $scope.playaudio.pause();
            $scope.playaudio.currentTime = 0;
        }

        function blobToFile(theBlob, fileName){
            //A Blob() is almost a File() - it's just missing the two properties below which we will add
            theBlob.lastModifiedDate = new Date();
            theBlob.name = fileName;
            return theBlob;
        }

        $scope.alerts = [];

    });
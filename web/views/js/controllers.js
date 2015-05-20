angular.module('sickBeetz.controllers', [])
    .controller('indexController', function($scope, $http, $modal, $anchorScroll, $location){
        var navigator = window.navigator;
        navigator.getUserMedia = (navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia);
        var Context = window.AudioContext || window.webkitAudioContext;
        var context = new Context();

        var mediaStream;
        var rec;

        $scope.kit='kit_2';

        var micVis = Object.create(WaveSurfer);
        micVis.init({
            container     : '#beatbox',
            waveColor     : 'red',
            interact      : false,
            cursorWidth   : 0
        });

        var microphone = Object.create(WaveSurfer.Microphone);
        microphone.init({
            wavesurfer: micVis
        });

        $scope.inpVis = Object.create(WaveSurfer);
        $scope.inpVis.init({
            container:'#waveform',
            waveColor:'grey',
            progressColor:'black'
        });

        $scope.outVis = Object.create(WaveSurfer);
        $scope.outVis.init({
            container:'#outputWav',
            wavecolor:'grey',
            progressColor:'black'
        });

        $scope.submitForm=function(){
            $scope.error = false;
            var file = $scope.input;
            var fd = new FormData();
            fd.append('file', file);
            fd.append('kit', $scope.kit);
            $scope.audiopath = undefined;
            $scope.submitted = true;

            //scroll to the appropriate part of the page
            $scope.scrollTo('step3');

            $http.post('/sickBeetz',fd,{
                transformReques: angular.identity,
                headers: {'Content-Type':undefined}
            }).then(function(res){
                console.log(res);
                $scope.audiopath = res.data.path;
                $scope.outVis.load(res.data.path);
            }, function(err){
                console.log(err);
                $scope.error = true
            });
        };

        $scope.record = function() {
            $scope.reset();

            var input = angular.element(document.getElementById('fileupload'));
            input.val(null);
            // ask for permission and start recording
            navigator.getUserMedia({audio: true}, function(localMediaStream){

                microphone.gotStream(localMediaStream);
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
                console.log(err)
                $modal.open({
                    animation: true,
                    templateUrl: 'err.html',
                    controller:'modalctrl'
                })
            });
        };

        $scope.stop = function() {
            $scope.recording = false;
            $scope.srcType='record';

            $scope.alerts.splice(0);
            $scope.alerts.push({type: 'success', msg: 'Audio Recorded Successfully!'});

            // stop the media stream
            mediaStream.stop();
            // stop Recorder.js
            rec.stop();
            microphone.stop();

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
                $scope.inpVis.loadBlob($scope.input)

                //scroll to the appropriate part of the page
                $scope.scrollTo('step2')

            });
        };

        $scope.scrollTo = function(id){
            $location.hash(id);
            $anchorScroll();
        };

        function blobToFile(theBlob, fileName){
            //A Blob() is almost a File() - it's just missing the two properties below which we will add
            theBlob.lastModifiedDate = new Date();
            theBlob.name = fileName;
            return theBlob;
        }

        $scope.alerts = [];

        $scope.reset = function(){
            $scope.alerts=[];
            $scope.error=false;
            $scope.audiopath="";
            $scope.submitted=false;
            $scope.recorded=false;
            $scope.input=undefined;
            $scope.srcType=undefined;
        };

        $scope.filePicked = function(){
            $scope.reset();
            $scope.srcType = 'file';
            $scope.$apply()
        };

        $scope.$watch('input',function(){
            if($scope.input == undefined){
                return
            }
            console.log($scope.input);
            $scope.inpVis.loadBlob($scope.input);
        });

        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'modal.html',
            controller:'modalctrl'
        })


    });

angular.module('sickBeetz.controllers').controller('modalctrl', function($scope, $modalInstance) {
        $scope.close = function () {
            $modalInstance.close();
        };
    });
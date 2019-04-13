'use strict';

/* Controllers */

var imageProcessingControllers = angular.module('imageProcessingControllers', []);

imageProcessingControllers.controller('PageController',
    ['$scope', '$translate', '$route', '$cookies', function ($scope, $translate, $route, $cookies) {
        var supportedLanguages = ['id', 'en'];
        var cookieLanguage = $cookies.language;

        if (cookieLanguage === undefined || supportedLanguages.indexOf(cookieLanguage) === 0) {
            // Set Indonesian as Default Language
            cookieLanguage = 'id';
            $cookies.language = cookieLanguage;
        }

        $translate.use(cookieLanguage);
        $scope.currentLangue = cookieLanguage;
        $scope.route = $route;

        // Switch Language Function
        $scope.switchLang = function (langKey) {
            $translate.use(langKey);
            $scope.currentLangue = langKey;
            $cookies.language = langKey;
        };
    }]);

imageProcessingControllers.controller('FormCarouselController',
    ['$scope', '$translate', function ($scope, $translate) {
        if ($translate.use() == 'en') {
            $scope.slides = [
                { image: 'img/forms/crumpled.jpg', text: 'Crumpled'},
                { image: 'img/forms/incorrectchecksum.jpg', text: 'Incorrectly counted'},
                { image: 'img/forms/inonecolumn.jpg', text: 'All numbers in one column'},
                { image: 'img/forms/corrected.jpg', text: 'Corrected'},
                { image: 'img/forms/tally.jpg', text: 'Tally'}
            ];
        } else {
            $scope.slides = [
                { image: 'img/forms/crumpled.jpg', text: 'Kusut'},
                { image: 'img/forms/incorrectchecksum.jpg', text: 'Salah hitung'},
                { image: 'img/forms/inonecolumn.jpg', text: 'Semua angka dalam satu kolom'},
                { image: 'img/forms/corrected.jpg', text: 'Koreksi angka'},
                { image: 'img/forms/tally.jpg', text: 'Turus'}
            ];

        }
    }]);

function getFileNames(numbers) {
    var fileNames = [];
    angular.forEach(numbers, function (number) {
        angular.forEach(number.extracted, function (extract) {
            fileNames.push(extract);
        });
    });
    return fileNames;
}

function getProbabilities(numbers) {
    var probalityList = [];
    angular.forEach(numbers, function (number) {
        var probabilities = [];
        angular.forEach(number.extracted, function (extract) {
            probabilities.push(extract.probabilities);
        });
        probalityList.push({id: number.id, probabilitiesForNumber: probabilities});
    });
    return probalityList;
}

imageProcessingControllers.controller('imageRegistrationController',
    ['$scope', '$http', '$document', function ($scope, $http, $document) {
        $document.bind("keypress", function(event) {
          if (event.charCode == 110) {
            $scope.stage +=1;
            console.debug($scope.stage);
            $scope.$apply();
          }
        });
        init();

        function init() {
            var placeHolderUrl = 'img/placeholder.jpg';
            $scope.uploadUrl = placeHolderUrl;
            $scope.progress = 0;
            $scope.numbers = null;
            $scope.extractedImages = [];
            $scope.signatures = [];
            $scope.Math = window.Math;
            $scope.registrationFailed = null;
            $scope.extractionFinished = false;
            $scope.mostProbableOutcome = null;
            $scope.tidakSah = null;
            $scope.correction = null;
            $scope.tidakSahCorrection = null;
            $scope.submitted = null;
            $scope.correct = null;
            $scope.digitArea = null;
            $scope.configFile = null;
            $scope.useKeyboardNavigation = false;
            $scope.stage = 0;
            return placeHolderUrl;
        }

        var placeHolderUrl = init();
        $scope.numbersAddUp = function () {
            if ($scope.mostProbableOutcome === null) {
                return true;
            }

            var total = $scope.mostProbableOutcome.map( x => x.number || 0);
            var summed = total.reduce(function(a,b) { return a + b; });
            var sum = total[total.length - 2];
            var addUp = (summed - sum) == sum;
            return addUp;
        };

        $scope.getToolTip = function (image) {
            if (image === undefined) {
                return '';
            }
            return "<img class='tooltipImage' src='" + image.filename + "' />";
        };

        function mostProbable(probabilities) {
            var mostProbable = '';
            angular.forEach(probabilities, function(probability, key) {
                if (probability > 0.02) {
                    var index = key == 10 ? 'X' : key;
                    mostProbable += ('<h4>' + index + ' - ' + Math.round(probability * 100) + '%</h4>');
                }
            });
            return mostProbable;
        }

        $scope.getConfidenceTooltip = function (image) {
            return "<div>" + mostProbable(image.probabilities) + "</div>";
        };

        $scope.hasUploadFinished = function () {
            return $scope.uploadUrl !== placeHolderUrl;
        };

        $scope.hasRegistrationFailed = function () {
            return $scope.registrationFailed === true;
        };

        $scope.isAreaSelected = function () {
            return $scope.digitArea !== null && (!$scope.useKeyboardNavigation || $scope.stage > 0);
        };

        $scope.hasExtractionSucceeded = function () {
            return $scope.hasUploadFinished() && !$scope.hasRegistrationFailed() &&
                $scope.extractedImages.length > 0 && (!$scope.useKeyboardNavigation || $scope.stage > 1);
        };

        $scope.hasExtractionFailed = function () {
            return $scope.hasUploadFinished() && $scope.hasRegistrationFailed() &&
                $scope.extractedImages.length === 0 && (!$scope.useKeyboardNavigation || $scope.stage > 1);
        };

        $scope.hasExtractionFinished = function () {
            return $scope.extractionFinished === true && (!$scope.useKeyboardNavigation || $scope.stage > 2);
        };

        $scope.abort = function () {
            init();
        };

        function enrichMostProbableOutcome(matrix) {
            var rows = [];
            angular.forEach(matrix, function(value) {
                rows.push(value);
            });
            return rows;
        }

        $scope.getResult = function (numbers) {
            var probabilities = getProbabilities(numbers);
            $http.post('../processprobs.wsgi', {
                probabilities: probabilities, configFile: $scope.configFile }).success(function (result) {
                $scope.mostProbableOutcome = enrichMostProbableOutcome(result.probabilityMatrix[0][0]);
                $scope.totals = enrichMostProbableOutcome(result.probabilityMatrix[1][0]);
                $scope.tidakSah = enrichMostProbableOutcome(result.probabilityMatrix[1][0]);
                $scope.probabilityMatrix = result.probabilityMatrix;
            });
        };

        $scope.disagree = function () {
            $scope.correction = angular.copy($scope.mostProbableOutcome);
            $scope.correctionTotals = angular.copy($scope.totals);
            $scope.tidakSahCorrection = angular.copy($scope.tidakSah);
        };

        $scope.agree = function () {
            $scope.correct = true;
        };

        $scope.submit = function () {
            $scope.submitted = true;
        };


        $scope.setImage = function (image) {
            var transformed = angular.fromJson(image);
            if (transformed === null) {
                return;
            }
            if (transformed.success === true) {
                $scope.uploadUrl = transformed.transformedUrl;
                $scope.uploadUri = transformed.transformedUri;
                $scope.configFile = transformed.configFile;
                $http.get('../extract.wsgi',
                    { params: { filename: $scope.uploadUri, configFile: $scope.configFile }}).success(function (result) {
                        $scope.extractedImages = getFileNames(result.numbers);
                        $scope.signatures = result.signatures;
                        $scope.registrationFailed = false;
                        $scope.digitArea = result.digitArea;
                        $scope.getResult(result.numbers);
                    }).error(function () {
                        $scope.registrationFailed = true;
                    });

            } else {
                $scope.uploadUrl = null;
                $scope.registrationFailed = true;
            }
            $scope.extractionFinished = true;

        };

        $scope.updateProgress = function (image) {
            if (image !== undefined) {
                $scope.progress = image.progress();
            }
        };
    }]);
'use strict';

/* Controllers */

var imageProcessingControllers = angular.module('imageProcessingControllers', []);

imageProcessingControllers.controller('PageController',
	['$scope', '$translate', '$route', '$cookies', function($scope, $translate, $route, $cookies) {
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
		$scope.switchLang = function(langKey) {
			$translate.use(langKey);
			$scope.currentLangue = langKey;	
			$cookies.language = langKey;
		};
	}]);

imageProcessingControllers.controller('FormCarouselController',
	['$scope', '$translate', function($scope, $translate) {
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

imageProcessingControllers.controller('imageRegistrationController',
	['$scope', '$http', function($scope, $http) {
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
		$scope.correction = null;
		$scope.submitted = null;
		$scope.correct = null;

		$scope.numbersAddUp = function() {
			if ($scope.mostProbableOutcome === null) {
				return true;
			}
			return ($scope.mostProbableOutcome.prabowo + $scope.mostProbableOutcome.jokowi) ===
				$scope.mostProbableOutcome.total;
		};

		$scope.getToolTip = function(image) {
			if (image === undefined) {
				return '';
			}
			return "<img class='tooltipImage' src='" + image.filename + "' />";
		};

		$scope.hasUploadFinished = function() {
			return $scope.uploadUrl !== placeHolderUrl;
		};

		$scope.hasRegistrationFailed = function() {
			return $scope.registrationFailed === true;
		};

		$scope.hasExtractionSucceeded = function() {
			return $scope.hasUploadFinished() && !$scope.hasRegistrationFailed() &&
				$scope.extractedImages.length > 0;
		};

		$scope.hasExtractionFailed = function() {
			return $scope.hasUploadFinished() && $scope.hasRegistrationFailed() &&
				$scope.extractedImages.length === 0;
		};

		$scope.hasExtractionFinished = function() {
			return $scope.extractionFinished === true;
		};

		$scope.abort = function() {
			location.reload();
		};

		$scope.getResult = function(probabilityMatrix) {
			$http.get('../processprobs.wsgi', {
				params: { probabilities: probabilityMatrix }}).success(function(result) {
				$scope.mostProbableOutcome = result.probabilityMatrix[0]
			});
		};

		$scope.disagree = function() {
			$scope.correction = angular.copy($scope.mostProbableOutcome);
		};

		$scope.agree = function() {
			$scope.correct = true;
		};

		$scope.submit = function() {
			$scope.submitted = true;
		};

		$scope.setImage = function(image) {
			var transformed = angular.fromJson(image);
			if (transformed === null) {
				return;
			}
			if (transformed.success === true) {
				$scope.uploadUrl = 'transformed/' + transformed.transformedUrl;
				$http.get('../extract.wsgi',
					{ params: { filename: $scope.uploadUrl }}).success(function(result) {
						$scope.extractedImages = result.digits;
						$scope.signatures = result.signatures;
						$scope.registrationFailed = false;
						$scope.getResult(result.probabilities);
					}).error(function() {
						$scope.registrationFailed = true;
					});

			} else {
				$scope.uploadUrl = null;
				$scope.registrationFailed = true;
			}
			$scope.extractionFinished = true;

		};

		$scope.updateProgress = function(image) {
			if (image !== undefined) {
				$scope.progress = image.progress();
			}
		};
	}]);
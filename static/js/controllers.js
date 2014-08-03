'use strict';

/* Controllers */

var imageProcessingControllers = angular.module('imageProcessingControllers', []);

imageProcessingControllers.controller('imageRegistrationController',
	['$scope', '$http', function($scope, $http) {
		var placeHolderUrl = 'img/placeholder.jpg';
		$scope.uploadUrl = placeHolderUrl; //UploadedImage.getUrl();
		$scope.progress = 0;
		$scope.numbers = null;
		$scope.extractedImages = [];
		$scope.Math = window.Math;
		$scope.registrationFailed = null;
		$scope.extractionFinished = false;


		$scope.hasUploadFinished = function() {
			return $scope.uploadUrl !== placeHolderUrl;
		};

		$scope.hasRegistrationFailed = function() {
			return $scope.registrationFailed === true;
		};

		$scope.hasExtractionSucceeded = function() {
			return $scope.hasUploadFinished() && !$scope.hasRegistrationFailed() && $scope.extractedImages.length > 0;
		};

		$scope.hasExtractionFailed = function() {
			return $scope.hasUploadFinished() && $scope.hasRegistrationFailed() && $scope.extractedImages.length === 0;
		};

		$scope.hasExtractionFinished = function() {
			return $scope.extractionFinished === true;
		};

		$scope.abort = function() {
			location.reload();
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
						$scope.extractedImages = result;
						$scope.registrationFailed = false;
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
		}

	}]);
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

		$scope.hasProcessStarted= function() {
			return $scope.uploadUrl !== placeHolderUrl;
		};

		$scope.setImage = function(image) {
			var transformed = angular.fromJson(image);
			if (transformed !== null) {
				$scope.uploadUrl = 'transformed/' + transformed.transformedUrl;
				$http.get('../extract.wsgi',
					{ params: { filename: $scope.uploadUrl }}).success(function(result) {
						$scope.extractedImages = result
					});

			}
		};

		$scope.updateProgress = function(image) {
			if (image !== undefined) {
				$scope.progress = image.progress();
			}
		}

	}]);
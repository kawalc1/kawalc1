'use strict';

/* Controllers */

var imageProcessingControllers = angular.module('imageProcessingControllers', []);

imageProcessingControllers.controller('imageRegistrationController',
	['$scope', '$http', function($scope, $http) {
		$scope.uploadUrl = null; //UploadedImage.getUrl();
		$scope.progress = 0;
		$scope.numbers = null;

		$scope.setImage = function(image) {
			var transformed = angular.fromJson(image);
			if (transformed !== null) {
				$scope.uploadUrl = 'transformed/' + transformed.transformedUrl;
				$http.get('../extract.wsgi',
					{ params: { filename: $scope.uploadUrl }}).success(function(data) {
						alert(data);
					});

			}
		};

		$scope.updateProgress = function(image) {
			if (image !== undefined) {
				$scope.progress = image.progress();
			}
		}

	}]);
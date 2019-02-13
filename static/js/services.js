'use strict';

/* Services */

var imageProcessingServices = angular.module('imageProcessingServices', ['ngResource']);

imageProcessingServices.factory('UploadedImage', ['$resource',
	function($resource){
		return {
			getUrl: function() {
				return 'upload/Tulips.jpg';
			}
		};
//		return $resource('phones/:phoneId.json', {}, {
//			query: {method:'GET', params:{phoneId:'phones'}, isArray:true}
//		});
	}]);

/*global angular */
'use strict';

/**
 * The main app module
 * @name app
 * @type {angular.Module}
 */
var app = angular.module('app',
	[	'flow',
		'imageProcessingControllers',
		'imageProcessingServices'
	]);

app.config(['flowFactoryProvider', function (flowFactoryProvider) {
		flowFactoryProvider.defaults = {
			target: '../transform.wsgi',
			permanentErrors: [404, 500, 501],
			maxChunkRetries: 1,
			progressCallbacksInterval: 100,
			speedSmoothingFactor: 0.02,
			chunkRetryInterval: 5000,
			simultaneousUploads: 4,
			singleFile: true
		};
		flowFactoryProvider.on('catchAll', function (event) {
			console.log('catchAll', arguments);
		});
		flowFactoryProvider.on('fileSuccess', function (file) {
			console.log('bladie', file.name);
		});
		// Can be used with different implementations of Flow.js
		// flowFactoryProvider.factory = fustyFlowFactory;
	}]);

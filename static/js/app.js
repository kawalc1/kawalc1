/*global angular */
'use strict';

/**
 * The main app module
 * @name app
 * @type {angular.Module}
 */
var app = angular.module('app',
	[    'flow', 'imageProcessingControllers', 'imageProcessingServices', 'pascalprecht.translate'
	]);

app.config(['flowFactoryProvider', function(flowFactoryProvider) {
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
	flowFactoryProvider.on('catchAll', function(event) {
		console.log('catchAll', arguments);
	});
	flowFactoryProvider.on('fileSuccess', function(file) {
		console.log('bladie', file.name);
	});
	// Can be used with different implementations of Flow.js
	// flowFactoryProvider.factory = fustyFlowFactory;
}]);

app.config(function($translateProvider) {
	$translateProvider.translations('en', {
		HEADLINE: 'Automated election form verification',
		TITLE: 'Automated election form verification',
		UPLOAD_TITLE: 'Upload form',
		UPLOAD_BUTTON: 'Browse',
		DETECTION_TITLE: 'Detect numbers',
		UPLOAD_ERROR_EXCUSE: 'Excuse me',
		UPLOAD_ERROR_DIAGNOSIS: 'it seems the numbers in the form could not be recognized.',
		UPLOAD_ERROR_SUGGESTION: 'Are you sure you uploaded the correct form?',
		VERIFICATION_TITLE: 'Verify data',
		SAMPLE_WARNING: 'Notice:',
		SAMPLE_MESSAGE: 'for now this data only serves as an example and is not detected from the form you uploaded.',
		BUTTON_CORRECT: 'Correct',
		BUTTON_NOT_CORRECT: 'Not Correct',
		CORRECTION_TITLE: 'Correct data',
		BUTTON_SEND: 'Send',
		BUTTON_RESTART: 'Upload another form',
		LINK_RESTART: 'Download example forms (1 MB)',
		SUBMITTED_THANKS: 'Thank you:',
		SUBMITTED_MESSAGE: 'the form has been submitted.'
	}).translations('id', {
		HEADLINE: 'Tukang Verifikator C1',
		TITLE: 'Tukang Verifikator C1',
		UPLOAD_TITLE: 'Unggah C1',
		UPLOAD_BUTTON: 'Pilih formulir',
		DETECTION_TITLE: 'Deteksi angka',
		UPLOAD_ERROR_EXCUSE: 'Mohon maaf',
		UPLOAD_ERROR_DIAGNOSIS: 'sepertinya angka2 dalam formulir ini tidak bisa terdeksi.',
		UPLOAD_ERROR_SUGGESTION: 'Apakah formulir ini memang formulir yang benar?',
		VERIFICATION_TITLE: 'Verifikasi data',
		SAMPLE_WARNING: 'Perhatian:',
		SAMPLE_MESSAGE: 'untuk sementara data ini hanya berfungsi sebagai contoh, dan bukan angka yang terdeksi dari formulir di sebelah ini.',
		BUTTON_CORRECT: 'Sesuai',
		BUTTON_NOT_CORRECT: 'Tidak Sesuai',
		CORRECTION_TITLE: 'Koreksi data',
		BUTTON_SEND: 'Kirim',
		BUTTON_RESTART: 'Unggah formulir lain',
		LINK_RESTART: 'Mengunduh formulir contoh (1 MB)',
		SUBMITTED_THANKS: 'Terima kasih:',
		SUBMITTED_MESSAGE: 'formulir C1 telah dikirim.'
	});
	$translateProvider.determinePreferredLanguage(function() {
		var browserLang = navigator.language.substr(0,2);
		return  browserLang === 'id' ? 'id': 'en';
	});

});

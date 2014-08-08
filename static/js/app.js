/*global angular */
'use strict';

/**
 * The main app module
 * @name app
 * @type {angular.Module}
 */
var app = angular.module('app',
	['flow', 'imageProcessingControllers', 'imageProcessingServices', 'pascalprecht.translate',
		'ngRoute'
	]);

app.config(function($routeProvider) {
	$routeProvider.when('/', {
		templateUrl: 'pages/home.html',
		controller: 'imageRegistrationController'
	}).when('/about', {
		templateUrl: 'pages/about.html'
	}).when('/contact', {
		templateUrl: 'pages/contact.html'
	});

});

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

	flowFactoryProvider.factory = fustyFlowFactory;
}]);

app.config(function($translateProvider) {
	$translateProvider.translations('en', {
		HEADLINE: 'Guarding C1',
		TITLE: 'Guarding C1 - Automatic verification of election forms',
		PAGE_HOME : 'Home',
		PAGE_ABOUT: 'About',
		PAGE_CONTACT: 'Contact',
		UPLOAD_TITLE: 'Upload form',
		UPLOAD_BUTTON: 'Browse',
		DETECTION_TITLE: 'Detect numbers',
		UPLOAD_CANCEL: 'Batal',
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
		HEADLINE: 'Kawal C1',
		TITLE: 'Kawal C1 - Verifikasi formulir secara otomatis',
		PAGE_HOME : 'Beranda',
		PAGE_ABOUT: 'Tentang',
		PAGE_CONTACT: 'Kontak',
		UPLOAD_TITLE: 'Unggah C1',
		UPLOAD_BUTTON: 'Pilih formulir',
		DETECTION_TITLE: 'Deteksi angka',
		UPLOAD_CANCEL: 'Batal',
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
		var navigator = window.navigator;
		var language = 'en-US';
		if (navigator.language !== undefined) {
			language = navigator.language;
		}
		if (navigator.userLanguage !== undefined) {
			language = navigator.userLanguage;
		}
		var browserLang = language.substr(0, 2);
		if (browserLang === 'id' || browserLang === 'ms') {
			return 'id';
		}
		return 'en';
	});

});

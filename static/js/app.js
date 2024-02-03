/*global angular */
'use strict';

/**
 * The main app module
 * @name app
 * @type {angular.Module}
 */
var app = angular.module('app',
	['flow', 'ui.bootstrap', 'imageProcessingControllers', 'imageProcessingServices',
		'pascalprecht.translate', 'ngRoute', 'ngCookies', 'ngAnimate'
	]);

app.config(function($routeProvider) {
	$routeProvider.when('/', {
		templateUrl: 'pages/home.html',
		controller: 'imageRegistrationController'
	}).when('/faq', {
		templateUrl: 'pages/faq.html'
	}).when('/about', {
		templateUrl: 'pages/about.html'
	}).when('/contact', {
		templateUrl: 'pages/contact.html'
	}).when('/page3', {
        templateUrl: 'pages/page3.html',
        controller: 'imageRegistrationController'
    }).when('/dpr', {
        templateUrl: 'pages/dpr.html',
        controller: 'imageRegistrationController'
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
		TITLE: 'Guarding C1 - Automatic Verification of Election Forms',
		VERSION: 'Version 1.2 - February 16, 2019',
		INTRODUCTION: 'This application counts election form results',
		INTRODUCTION_TRYIT: 'Try with ',
		INTRODUCTION_TRYIT_LINK_1 : 'form 1',
		INTRODUCTION_TRYIT_LINK_2 : 'form 2',
		PAGE_HOME: 'Home',
		PAGE_ABOUT: 'About',
		PAGE_FAQ: 'FAQ',
		PAGE_CONTACT: 'Contact',
		UPLOAD_TITLE: 'Upload Form',
		UPLOAD_BUTTON: 'Browse',
		DETECTION_TITLE: 'Detect Numbers',
		UPLOAD_CANCEL: 'Cancel',
		UPLOAD_ERROR_EXCUSE: 'Excuse me',
		UPLOAD_ERROR_DIAGNOSIS: 'it seems the numbers in the form could not be recognized.',
		UPLOAD_ERROR_SUGGESTION: 'Are you sure you uploaded the correct form?',
		VERIFICATION_TITLE: 'Verify Data',
		SAMPLE_WARNING: 'Notice:',
		SAMPLE_MESSAGE: 'currently this software still has problems detecting crosses.',
		BUTTON_CORRECT: 'Correct',
		BUTTON_NOT_CORRECT: 'Not Correct',
		CORRECTION_TITLE: 'Correct Data',
		BUTTON_SEND: 'Send',
		BUTTON_RESTART: 'Upload another form',
		LINK_DOWNLOAD_FORMS: 'old ones',
		SUBMITTED_THANKS: 'Thank you:',
		SUBMITTED_MESSAGE: 'the form has been submitted.',
		FORM_CANDIDATE: 'Candidate',
		FORM_TOTAL: 'Total',
		FORM_VOTES_INVALID: 'Invalid votes',
		FORM_VOTES_VALID: 'Total valid votes',
		FORM_VOTES_TOTAL: 'Total votes altogether',
		WITNESS_SIGNATURES: 'Witness signatures',
		SIGNATURE_PRESENT: 'Present',
		SIGNATURE_ABSENT: 'Missing',
        NEW_ALERT: 'New! 2019',
        TRY_THESE: 'Try it with',
        TRY_NEW_FORMS: 'new C1 plano forms',
        TRY_OLD_FORMS: 'or these'

	}).translations('id', {
		HEADLINE: 'Kawal C1',
		TITLE: 'Kawal C1 - Verifikasi Formulir Secara Otomatis',
		VERSION: 'Versi 1.3 - 20 Jan, 2024',
		INTRODUCTION: 'Aplikasi ini menghitung otomatis formulir C1',
		INTRODUCTION_TRYIT: 'Coba dengan ',
		INTRODUCTION_TRYIT_LINK_1 : 'formulir 1',
		INTRODUCTION_TRYIT_LINK_2 : 'formulir 2',
		PAGE_HOME: 'Beranda',
		PAGE_ABOUT: 'Tentang',
		PAGE_FAQ: 'FAQ',
		PAGE_CONTACT: 'Kontak',
		UPLOAD_TITLE: 'Unggah C1',
		UPLOAD_BUTTON: 'Pilih Formulir',
		DETECTION_TITLE: 'Deteksi Angka',
		UPLOAD_CANCEL: 'Batal',
		UPLOAD_ERROR_EXCUSE: 'Mohon maaf',
		UPLOAD_ERROR_DIAGNOSIS: 'sepertinya angka2 dalam formulir ini tidak bisa terdeksi.',
		UPLOAD_ERROR_SUGGESTION: 'Apakah formulir ini memang formulir yang benar?',
		VERIFICATION_TITLE: 'Verifikasi Data',
		SAMPLE_WARNING: 'Perhatian:',
		SAMPLE_MESSAGE: 'saat ini aplikasi ini masih bermasalah dalam mendeteksi X.',
		BUTTON_CORRECT: 'Sesuai',
		BUTTON_NOT_CORRECT: 'Tidak Sesuai',
		CORRECTION_TITLE: 'Koreksi Data',
		BUTTON_SEND: 'Kirim',
		BUTTON_RESTART: 'Unggah formulir lain',
		LINK_DOWNLOAD_FORMS: 'lama ini',
		SUBMITTED_THANKS: 'Terima kasih:',
		SUBMITTED_MESSAGE: 'formulir C1 telah dikirim.',
		FORM_CANDIDATE: 'Calon',
		FORM_TOTAL: 'Jumlah',
		FORM_VOTES_INVALID: 'Suara tidak sah',
		FORM_VOTES_VALID: 'Jumlah suara sah',
		FORM_VOTES_TOTAL: 'Jumlah seluruhnya',
		WITNESS_SIGNATURES: 'Tanda tangan saksi',
		SIGNATURE_PRESENT: 'Ada',
		SIGNATURE_ABSENT: 'Tidak ada',
        NEW_ALERT: 'Baru!!! 2024',
        TRY_THESE: 'Cobalah dengan',
        TRY_NEW_FORMS: 'formulir plano C1',
        TRY_OLD_FORMS: 'atau yang '
	});
});

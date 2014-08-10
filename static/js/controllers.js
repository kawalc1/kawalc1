'use strict';

/* Controllers */

var imageProcessingControllers = angular.module('imageProcessingControllers', []);
var matrix =
		[
			[0.0003282389952801168, 0.9497349858283997, 0.001507019973360002,
				0.005978509783744812, 0.00037203601095825434, 0.0001852020068326965,
				0.0006536139990203083, 0.0009307899745181203, 0.019562700763344765,
				0.0007565509877167642, 0.019990600645542145],
			[0.00010414199641672894, 0.5789830088615417, 0.0007795789861120284,
				0.000714352005161345, 0.0010718900011852384, 0.0009748089942149818,
				0.0025737599935382605, 0.0011571700451895595, 0.009860590100288391,
				0.0008730160188861191, 0.40290799736976624],
			[0.0013175900094211102, 0.010882900096476078, 0.09385280311107635,
				0.13251300156116486, 6.155839855637169e-07, 0.00027786201098933816,
				9.277409844798967e-05, 0.24241699278354645, 0.0005040480173192918,
				0.0013261500280350447, 0.5168160200119019],
			[0.000699141004588455, 0.17064599692821503, 0.009154490195214748,
				0.011481000110507011, 0.00020055299683008343, 0.00038877601036801934,
				0.0006073269760236144, 0.005841500125825405, 0.02598460018634796,
				0.0018388299504294991, 0.773157000541687],
			[0.0037870800588279963, 0.0007059599738568068, 0.005047639831900597,
				0.021045800298452377, 3.715569982887246e-05, 0.005020549986511469,
				0.0005095539963804185, 1.8852499579224968e-06, 0.7259899973869324,
				0.001195620046928525, 0.2366580069065094],
			[5.504249998011801e-07, 6.76540992117225e-08, 1.99842997972155e-05,
				9.771870099939406e-05, 5.752970082539832e-06, 1.3145199773134664e-06,
				0.9998599886894226, 6.7973799922071976e-09, 7.575859854114242e-06,
				3.655290070625483e-09, 6.993249826336978e-06],
			[2.0910499642923241e-07, 1.0046200031865737e-06, 0.0004993039765395224,
				0.9979709982872009, 2.7767100618802942e-08, 5.439819869934581e-05,
				4.854689905187115e-06, 3.16943010147952e-06, 3.239779971409007e-06,
				7.215769983304199e-06, 0.001455600024200976],
			[0.997767984867096, 1.2721499842882622e-05, 0.001457239966839552,
				3.188820119248703e-05, 9.745549789386132e-08, 0.00021727099374402314,
				4.9585100896365475e-06, 6.895219848956913e-05, 3.047910013265209e-08,
				4.396530130179599e-05, 0.0003944369964301586],
			[1.1193300451850519e-05, 7.0750202212366275e-06, 0.000154879002366215,
				0.9993929862976074, 8.615869973027657e-08, 6.973379640839994e-05,
				1.9060199747400475e-06, 5.90701984037878e-06, 9.894850336422678e-06,
				1.9902499843738042e-05, 0.00032612698851153255],
			[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
			[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
			[2.5612200261093676e-05, 0.00018012999498751014, 0.9844740033149719,
				0.0009637019829824567, 1.0869199940088947e-07, 1.3991500509291654e-06,
				5.420829893409973e-06, 1.7058100638678297e-05, 0.0012140900362282991,
				1.866429920482915e-05, 0.013099499978125095]
		];

imageProcessingControllers.controller('PageController', ['$scope', '$translate', '$route', function($scope, $translate, $route) {
	$scope.currentLangue = $translate.use();
	$scope.route = $route;
	$scope.switchLang = function(langKey) {
		$translate.use(langKey);
		$scope.currentLangue = langKey;
	};
}]);

imageProcessingControllers.controller('imageRegistrationController',
	['$scope', '$http', function($scope, $http) {
		var placeHolderUrl = 'img/placeholder.jpg';
		$scope.uploadUrl = placeHolderUrl; //UploadedImage.getUrl();
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

		$scope.getToolTip = function(image){
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

		$scope.getResult = function() {
			$http.get('../processprobs.wsgi', {
				params : { probabilities : matrix }}).success(function(result) {
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
						$scope.getResult();
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
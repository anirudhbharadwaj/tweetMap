
			function radioChange(elt)	{
				var sel = $(elt).data('title');
				var tog = $(elt).data('toggle');
				$('#'+tog).prop('value', sel);
				$('a[data-toggle="'+tog+'"]').not('[data-title="'+sel+'"]').removeClass('active').addClass('notActive');
				$('a[data-toggle="'+tog+'"][data-title="'+sel+'"]').removeClass('notActive').addClass('active');
				if(sel=="1")
					pin();
				else
					heat();
			}
		
			var map,heatmap,isnormal,lat,lng,dist, name ,text;
			var tweetData=[];
			var nameArray = [];
			var textArray = [];
			var dateArray = [];
			var screenNameArray= [];
			var currPosition=new Array(20,20);
			function initialize() {
				if(currPosition != null)	{
					var myCenter=new google.maps.LatLng(currPosition[0],currPosition[1]);
					var mapProp = {
					center:myCenter,
					styles: [{"featureType":"all","elementType":"labels.text.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"all","elementType":"labels.text.stroke","stylers":[{"color":"#000000"},{"lightness":13}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#144b53"},{"lightness":14},{"weight":1.4}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#08304b"}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#0c4152"},{"lightness":5}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#0b434f"},{"lightness":25}]},{"featureType":"road.arterial","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.arterial","elementType":"geometry.stroke","stylers":[{"color":"#0b3d51"},{"lightness":16}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#000000"}]},{"featureType":"transit","elementType":"all","stylers":[{"color":"#146474"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#021019"}]}],
					zoom:2,
					mapTypeId:google.maps.MapTypeId.ROADMAP
					};
					map=new google.maps.Map(document.getElementById("googleMap"),mapProp);
					google.maps.event.addListener(map, "rightclick", function(event) {
						document.getElementById('isnormal').value="1";
						submitForm(document.getElementById('sel1'));
					});
					google.maps.event.addListener(map, "click", function(event) {
						document.getElementById('isnormal').value="2";
						document.getElementById('lat').value=event.latLng.lat();
						document.getElementById('lng').value=event.latLng.lng();
						submitForm(document.getElementById('sel1'));
					});
					if(isnormal=="2")	{
						var myCity = new google.maps.Circle({
							map: map,
							strokeColor: '#f0ffff',
							strokeOpacity: 0.8,
							strokeWeight: 2,
							fillColor: '#000f0f',
							fillOpacity: 0.25,
							center: new google.maps.LatLng(parseInt(lat), parseInt(lng)),
							radius: parseInt(dist) * 1000
						});
					}
				}
			}

			function submitForm(element){
				element.form.submit();
			}
			
			var entityMap = {
			  "&": "&amp;",
			  "<": "&lt;",
			  ">": "&gt;",
			  '"': '&quot;',
			  "'": '&#39;',
			  "/": '&#x2F;'
			};

			function escapeHtml(string) {
			  return String(string).replace(/[&<>"'\/]/g, function (s) {
				return entityMap[s];
			  });
			}
			function isNumber(evt) {
				evt = (evt) ? evt : window.event;
				var charCode = (evt.which) ? evt.which : evt.keyCode;
				if (charCode > 31 && (charCode < 48 || charCode > 57)) {
					return false;
				}
				return true;
			}
			function renderTweets(list)	{
				initialize();
				if(!(list == null || list.length==0))	{
					var res = JSON.parse(list);
					var searchKey=res['search_key'];
					$("#sel1").val(searchKey);
					var type_txt=res['type_txt'];
					dist=res['dist'];
					$("#distance").val(parseInt(dist));
					isnormal=res['isnormal'];
					lat=res['lat'];
					lng=res['lng'];
					text = res['text'];
					name = res['name'];
					$("#isnormal").val(isnormal);
					$("#lat").val(lat);
					$("#lng").val(lng);
					if(res['message']=="SUCCESS")	{
						var data=res['result'];
						var size=0;
						if(data!=null)	{
							size=data.length;
							for(var i = 0; i < data.length; i++) {
								var obj = JSON.parse(data[i]);
								tweetData[i] = new google.maps.LatLng(obj['latitude'], obj['longitude']);
								nameArray[i] = obj['name'];
								textArray[i] = obj['text'];
								screenNameArray[i] = obj['userScreenName'];
								dateArray[i] = obj['date'];
							}
							if(type_txt=="1")	{
								radioChange(document.getElementById('pts'));
							}
							else	{
								radioChange(document.getElementById('hts'));
							}
						}
						 $('#successtxt').html(" "+size+ " results found for " +searchKey);
						 $('#alertsuccess').show();
					}
				}
			}
			
			function pin() {
				initialize();
				var markers = [];
				var image = 'http://www.stalbertgazette.com/assets/images/hockeypool/twitterIcon.png';
				var infowindow = new google.maps.InfoWindow({
					content: "holding..."
				});
				for (i = 0; i < tweetData.length; i++) {
					var contentString = '<div><h3>'+nameArray[i]+'</h3>'+'<h4>@'+screenNameArray[i]+'</h4>'+'<div>'+'<p>'+textArray[i]+'</p>'+'<p>(Tweeted '+dateArray[i]+')</p>'+'</div>'+'</div>';
					marker = new google.maps.Marker({
						animation: google.maps.Animation.DROP,
						icon: image,
						position: tweetData[i],
						map: map,
						text : contentString
					});
					google.maps.event.addListener(marker, 'click', function () {
						infowindow.setContent(this.text);
						infowindow.open(map, this);
					});
					markers.push(marker);
				}
				var markerCluster = new MarkerClusterer(map, markers,{imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});
			}
			
			function heat() {
				initialize();
				heatmap = new google.maps.visualization.HeatmapLayer({
					data: new google.maps.MVCArray(tweetData),
					radius: 25,
					map: map
				});
			}
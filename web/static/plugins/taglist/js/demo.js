(function( $ ) {
	$( document ).ready( function() {
		$( '#email-list' ).tagList( 'create', {
			tagValidator : function( emailid ) {
				// @warning: not sure if this RegExp is good enough for all types of email ids
				var emailPat = /^[A-Za-z]+[A-Za-z0-9._]*@[A-Za-z0-9]+\.[A-Za-z.]*[A-Za-z]+$/;
				return emailPat.test( $.trim( emailid ) );
			}
		});
		
		$( '#mobile-number-list' ).tagList( 'create', {
			tagValidator : function( mobileNumber ) {
				var mobileNumberPat = /^[1-9]{1}[0-9]{9}$/;
				return mobileNumberPat.test( $.trim( mobileNumber ) );
			}
		});

		$( '#email-list' ).on( 'tagadd', function( $event, tagText, opStatus, message ) {
			if( opStatus === 'success' ) {
				console.log( 'Email \'' + tagText + '\' added' );
			} else if( opStatus === 'failure' ) {
				alert( 'Email \'' + tagText + '\' could not be added [' + message + ']' );
			}
		});
		
		$( '#email-list, #mobile-number-list' ).on( 'tagremove', function( $event, tagText ) {
			console.log( 'Tag \'' + tagText + '\' removed' );	
		});
	});
}( jQuery ));
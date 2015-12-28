
/* this class implements a simple wrapper which fetches a URL, parses it and returns a 
 * JSON object. For use within XSLT.
 * depends on jakarta commons-logging, commons-httpclient and commons-codec
 */
package org.spl.utils;

import org.json.*;
import org.apache.commons.httpclient.*;
import org.apache.commons.httpclient.cookie.CookiePolicy;
import java.util.*;
import java.io.*;

public class Utils {
	private static HttpClient client;
	private static MultiThreadedHttpConnectionManager connectionManager;
	private static Properties props;
	private static String encoding;
	
	private static synchronized HttpClient getHttpClient() {
		
		if( connectionManager == null ) {
			// load properties file
			props = new Properties();
			FileInputStream fis;
			try {
				fis = new FileInputStream("getURL.properties");
				props.load( fis );
				fis.close();
			} catch( IOException e ) {
				e.printStackTrace();
			}
			String loglevel = props.getProperty("loglevel", "error");
			int timeout = Integer.parseInt( props.getProperty("connectionTimeout", "0") );			
			
			int maxTotalConnections = Integer.parseInt( props.getProperty("maxTotalConnections", "20"));
			
			encoding = props.getProperty("defaultEncoding", "");
			
			System.setProperty("org.apache.commons.logging.Log", "org.apache.commons.logging.impl.SimpleLog");
			System.setProperty("org.apache.commons.logging.simplelog.showdatetime", "true");
			System.setProperty("org.apache.commons.logging.simplelog.log.org.apache.commons.httpclient", loglevel);
			
			// TODO: set max retries here?
			System.err.println(">>>initializing connection manager and client..."); 
			connectionManager = new MultiThreadedHttpConnectionManager();
			connectionManager.getParams().setConnectionTimeout(timeout);
			connectionManager.getParams().setTcpNoDelay(true);
			connectionManager.getParams().setMaxTotalConnections(maxTotalConnections);
			client = new HttpClient(connectionManager);
		}
		return client;
	}
	
	public static String getURL(String URLName){
	       //StringBuffer response = new StringBuffer();
		   String response = "";
		   //HttpClient client= new HttpClient();
		   HttpClient client = getHttpClient();
		  // client.getHttpConnectionManager().getParams().setConnectionTimeout( 500 );
	       
		   org.apache.commons.httpclient.methods.GetMethod method = null;
		   method = new org.apache.commons.httpclient.methods.GetMethod( URLName );
		   method.setFollowRedirects(true);
		   
		   // this may give a slight performance boost.
		   method.getParams().setCookiePolicy(CookiePolicy.IGNORE_COOKIES);
	       
		   try {
			   client.executeMethod( method );
               // TODO: check for invalid http response code

			   byte[] responseBody = method.getResponseBody();
               
               int statusCode = method.getStatusCode();
               if( statusCode == 404 || statusCode == 503 || statusCode == 500 ) {
                   System.err.println("Got status code " + statusCode + " for request "  + URLName + "." );
                   // we will return a null response here rather than return the error page that was just fetched.  
               } else {
                   if( encoding.length() > 0 ) {
                       response = new String(responseBody, encoding );
                   } else {
                       // no encoding specified -- use web server's preference.
                       response = new String( responseBody, method.getResponseCharSet() );
                   }
               }
		   } catch(Exception e) {
			   e.printStackTrace();
		   } finally {
			   method.releaseConnection();
		   }
	       return response;
	}
	public static JSONObject getJSON( String URLName ) {
		JSONObject jso = null;
		String resp = "";
		try {
			resp = getURL( URLName );
			jso = new JSONObject( resp );
		} catch(Exception e) {
			e.printStackTrace();
			jso = new JSONObject();
		}
		return jso;
	}
	

}

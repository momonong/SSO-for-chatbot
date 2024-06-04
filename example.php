<!-- HTML................略 -->

<?php
/* OAuth Start  */

//這行一定要加上去，目的取得REQUEST_TIME控制token取得
define('REQUEST_TIME', (int) $_SERVER['REQUEST_TIME']);

//設定哪裡取得oauth2_client class 
include("oauth2_client/oauth2_client.inc");

/**
 * 下面設定與OAuth Server 溝通的參數， 
 *   $base_url 改成自己的Web Server Domain
 *   client_id 改成由OAuth管理員授權的client_id
 *   client_secret 改成申請的系統代碼
 *   redirect_uri 改成申請的redirect_uri
 * 
 *   參數:'nckusso' 需要改為個人申請的app的名稱     
 */
$base_url = "https://i.ncku.edu.tw";
$server_url = "https://fs.ncku.edu.tw";
$oauth2_clients['nckusso'] = array(
    'token_endpoint' => $server_url . '/adfs/oauth2/token',
    'auth_flow' => 'server-side',
    'client_id' => 'c5e***a5-3*0d-*b17-b**3-e2ab*e88*751',
    'client_secret' => 'nckusso',
    'authorization_endpoint' => $server_url . '/adfs/oauth2/authorize',
    'redirect_uri' => $base_url . '/ncku/tfcfd_dev/service/login.php',
);



// NEW一個 oauth2_client 物件
$oauth2_client = new OAuth2\Client($oauth2_clients['nckusso'], 'nckusso');

//先清除Token
$oauth2_client->clearToken();

//在輸入帳號密碼完成授權後會回傳accessToken
$access_token = $oauth2_client->getAccessToken();

/**
 * 利用accessToken 轉換為可讀的資料，回傳 array , 回傳範例如下
 *   $result['commonname'] = "S26051017"
 *   $result['DN'] = "CN=S26051017,OU=Students,DC=ncku,DC=edu,DC=tw"
 *   $result['email'] = "s26051017@ncku.edu.tw"
 *   $result['identity'] =  "student" 或 "staff"
 */
$result = $oauth2_client->getUserIdentity($access_token);

//自行處理登入系統身份識別，可利用 $result['identity'] 先判別學生或職員
//其他識別是否有權限使用系統，可以將原先判別的程式寫在這裡
$chklogin = FALSE;
if (isset($result['commonname'])) {
    (isset($_SESSION["Tstuno"]) ? session_destroy() : '');
    if ($result['identity'] == 'student') {
        //成功後寫入$_SESSION[''] 與之前系統判別做銜接，正確銜接上後就可以不用修訂原系統程式。
        //這部分請大家自行控制
        $_SESSION['Tstuno'] = trim($result['commonname']);
        $chklogin = TRUE;
    } else { // 非學生身份
        $oauth2_client->clearToken();
        echo ($langc['NOACCESS']);
        echo "<br>";
        echo ($langc['CLOSEWINDOW']);
        die;
    }
} else { // 驗證不過就導到其他網頁處理
    $oauth2_client->clearToken();
    echo ($langc['PASSWD_ERR']);
    echo ("<a href=http://" . $_SERVER['HTTP_HOST'] . dirname($_SERVER['PHP_SELF']) . "/" . "login_m.php>{$langc['LOGOIN_AGAIN']}</a>" );
    die;
}
/* OAuth2 End */

// 下面認證授權通過後即可處理系統內部的流程

//EX:跑流程～取得學年學期......
$rs = getYearSemVal();
$Nowtime = date("Y") - 1911 . date("md");
$Nowtime = substr('0' . $Nowtime, -7);

?>
<!-- ....................略～ -->





<?php

namespace OAuth2;
//ini_set('display_errors', 1);
//ini_set('display_startup_errors', 1);
//error_reporting(E_ALL);
/**
 * @file
 * class OAuth2\Client
 * Ver: 1.3 
 * 2017/6/13 增加 identity 屬性判斷學生(student)或職員(staff)
 * 2017/8/23 修改 getUserIdentity() JWT decode Bug(修改特殊字元造成誤判的問題)
 * 2017/9/13 修改 resource 有 '~' 號問題
 * 2017/9/19 修正 中文亂碼問題
 */
class Client {

    /**
     * Unique identifier of an OAuth2\Client object.
     */
    protected $id = NULL;

    /**
     *  - token_endpoint :: something like:
     *       https://oauth2_server.example.org/oauth2/token
     *  - authorization_endpoint :: somethig like:
     *       https://oauth2_server.example.org/oauth2/authorize
     *  - redirect_uri :: something like:
     *       https://oauth2_client.example.org/oauth2/authorized
     *  - scope :: requested scopes, separated by a space
     */
    protected $params = array(
        'auth_flow' => NULL,
        'client_id' => NULL,
        'client_secret' => NULL,
        'token_endpoint' => NULL,
        'authorization_endpoint' => NULL,
        'redirect_uri' => NULL,
        'proxy_server' => NULL
    );

    /**
     * Associated array that keeps data about the access token.
     */
    protected $token = array(
        'access_token' => NULL,
        'expires_in' => NULL,
        'token_type' => NULL,
        'scope' => NULL,
        'refresh_token' => NULL,
        'expiration_time' => NULL,
    );

    /** Return the token array. */
    function token() {
        return $this->token;
    }

    /**
     * Construct an OAuth2\Client object.
     *
     * @param array $params
     *
     * @param string $id
     */
    public function __construct($params = NULL, $id = NULL) {
//        echo "__construct";
         if ($params)
            $this->params = $params + $this->params;

//        var_dump($params);
//        exit;

        if (!$id) {
            $id = md5($this->params['token_endpoint']
                    . $this->params['client_id']
                    . $this->params['auth_flow']);
        }
        $this->id = $id;

        // Get the token data from the session, if it is stored there.
        if (isset($_SESSION['oauth2_client']['token'][$this->id])) {
            $this->token = $_SESSION['oauth2_client']['token'][$this->id] + $this->token;
        }
    }

    /**
     * Clear the token data from the session.
     */
    public function clearToken() {
        if (isset($_SESSION['oauth2_client']['token'][$this->id])) {
            unset($_SESSION['oauth2_client']['token'][$this->id]);
        }
        $this->token = array(
            'access_token' => NULL,
            'expires_in' => NULL,
            'token_type' => NULL,
            'scope' => NULL,
            'refresh_token' => NULL,
            'expiration_time' => NULL,
        );
    }

    /**
     * Get and return an access token.
     *
     * 1.如果token 存在session中,取出session中的. 假如 token 過期，
     * 從 authorization server  取新的。
     *
     * 2.假如refresh_token 也過期，會重新驗證.
     * 
     */
    public function getAccessToken($redirect = TRUE) {
        //檢查是否有存在的token，通常1hr過期，所以設定10sec內的
        //取token就直接回傳，避免重複取用。
        $expiration_time = $this->token['expiration_time'];

        if ($expiration_time > (time() + 10)) {
            return $this->token['access_token'];
        }

        try {
            // Try to use refresh_token.
            $token = $this->getTokenRefreshToken();
//            var_dump($token);
//            exit;
        } catch (\Exception $e) {
            // Get a token.
            switch ($this->params['auth_flow']) {
                case 'server-side':
                    if ($redirect) {
                        $token = $this->getTokenServerSide();
                    } else {
                        $this->clearToken();
                        return NULL;
                    }
                    break;
                case 'proxy-side':
//                    if($this->params['proxy_server'])
//                    $encode =  $this->params['client_id'];
//                    header('Location:' . $param)
                    var_dump($this->params['proxy_server']);
                    exit;
                    break;
                default:
     throw new \Exception("Unknown authorization flow " . $this->params['auth_flow'] . " Suported values for auth_flow are:server-side.");
                    break;
            }
        }

        $token['expiration_time'] = REQUEST_TIME + $token['expires_in'];

        // Store the token (on session as well).
        $this->token = $token;
        $_SESSION['oauth2_client']['token'][$this->id] = $token;

        // Redirect to the original path (if this is a redirection
        // from the server-side flow).
        self::redirect();

        // Return the token.
//        dpm($token['access_token']);
        return $token['access_token'];
    }

    /**
     * Get a new access_token using the refresh_token.
     *
     * This is used for the server-side
     */
    protected function getTokenRefreshToken() {
        if (!$this->token['refresh_token']) {
            throw new \Exception('There is no refresh_token.');
        }
        return $this->getToken(array(
                    'grant_type' => 'refresh_token',
                    'refresh_token' => $this->token['refresh_token'],
        ));
    }

    /**
     * Get an access_token using the server-side (authorization code) flow.
     *
     *     $access_token = $client->getAccessToken();
     * or:
     *     $client = new OAuth2\Client(array(
     *         'token_endpoint' => 'https://oauth2_server/oauth2/token',
     *         'client_id' => 'client1',
     *         'client_secret' => 'secret1',
     *         'auth_flow' => 'server-side',
     *         'authorization_endpoint' => 'https://oauth2_server/oauth2/authorize',
     *         'redirect_uri' => 'https://oauth2_client/oauth2/authorized',
     *       ));
     *     $access_token = $client->getAccessToken();
     *
     */
    protected function getTokenServerSide() {

//        var_dump($_GET['state']);

        if (!isset($_GET['code'])) {
            $url = $this->getAuthenticationUrl();
            header('Location: ' . $url, TRUE, 302);
            exit;
//            drupal_exit($url);
        } else {
            // Check the query parameter 'state'.
//            if (!isset($_GET['state']) || !isset($_SESSION['oauth2_client']['redirect'][$_GET['state']])) {
//                throw new \Exception("Wrong query parameter 'state'.");
//            }
//                        var_dump($_GET);
//            exit;
            // Get and return a token.
            return $this->getToken(array(
                        'client_id' => $this->params['client_id'],
                        'grant_type' => 'authorization_code',
                        'code' => $_GET['code'],
                        'redirect_uri' => $this->params['redirect_uri'],
            ));
        }
    }

    /**
     * Return the authentication url (used in case of the server-side flow).
     */
    protected function getAuthenticationUrl() {
        $state = md5(uniqid(rand(), TRUE));
        $query_params = array(
            'response_type' => 'code',
            'client_id' => $this->params['client_id'],
            'redirect_uri' => $this->params['redirect_uri'],
            'state' => $state,
            'resource' => str_replace("~", "", $this->params['redirect_uri'])
        );

        $endpoint = $this->params['authorization_endpoint'];

        return $endpoint . '?' . http_build_query($query_params);
    }

    /**
     * Save the information needed for redirection after getting the token.
     */
    public static function setRedirect($state, $redirect = NULL) {
        if ($redirect == NULL) {
            $redirect = array(
                'uri' => $_GET['q'],
                'params' => drupal_get_query_parameters(),
                'client' => 'oauth2_client',
            );
        }
        if (!isset($redirect['client'])) {
            $redirect['client'] = 'external';
        }
        $_SESSION['oauth2_client']['redirect'][$state] = $redirect;
    }

    /**
     * Redirect to the original path.
     *
     * Redirects are registered with OAuth2\Client::setRedirect()
     * The redirect contains the url to go to and the parameters
     * to be sent to it.
     */
    public static function redirect($clean = TRUE) {
        if (!isset($_REQUEST['state']))
            return;
        $state = $_REQUEST['state'];

        /*
         *  修改已經登出後還留state但是session已經清除的問題。
         *  重新導入到<front>首頁頁面
         */

        if (!isset($_SESSION['oauth2_client']['redirect'][$state])) {
//            header($string);
            return;
        }
    }

    /**
     * Get and return an access token for the grant_type given in $params.
     */
    protected function getToken($data) {

//        drupal_set_message('##getToken');
//        dpm($data);

        $token_endpoint = $this->params['token_endpoint'];

        $responseJson = $this->postData($token_endpoint, $data);

        $result = (Array) json_decode($responseJson, TRUE);

//        dpm($result);
        return $result;
    }

    protected function postData($url, $postData) {
        $ch = curl_init();
        $query = "";

        while (list($key, $val) = each($postData)) {
            if (strlen($query) > 0) {
                $query = $query . '&';
            }
            $query = $query . $key . '=' . $val;
        }

//        var_dump($postData);
//        exit;
        $options = array(
            CURLOPT_URL => $url,
            CURLOPT_SSL_VERIFYHOST => 0,
            CURLOPT_SSL_VERIFYPEER => 0,
            CURLOPT_FOLLOWLOCATION => 1,
            CURLOPT_RETURNTRANSFER => TRUE,
            CURLOPT_POST => TRUE,
            CURLOPT_POSTFIELDS => $query);

        curl_setopt_array($ch, $options);

//        print_r($options);
//        exit;

        $response = curl_exec($ch);


// ------logout.php 範例 ------
<?php
/* OAuth Start  
 * 
 * 參數:'nckusso' 需要改為個人申請的app的名稱  
 *  */
define('REQUEST_TIME', (int) $_SERVER['REQUEST_TIME']);
include("oauth2_client/oauth2_client.inc");
$base_url = "https://i.ncku.edu.tw";
$server_url = "https://fs.ncku.edu.tw";
$oauth2_clients['nckusso'] = array(
    'token_endpoint' => $server_url . '/adfs/oauth2/token',
    'auth_flow' => 'server-side',
    'client_id' => 'c5e***a5-3*0d-*b17-b**3-e2ab*e88*751',
    'client_secret' => 'nckusso',
    'authorization_endpoint' => $server_url . '/adfs/oauth2/authorize',
    'redirect_uri' => $base_url . '/ncku/tfcfd_dev/service/login.php',
);

$oauth2_client = new OAuth2\Client($oauth2_clients['nckusso'], 'nckusso');

//logout 動作如下

// Step 1. 清除此APP New 出來的SESSION
unset($SESSION['This App Session']);

// Step 2. 清除 oauth 在client端 New 出來的SESSION
$oauth2_client->clearToken();

// Step 3. 清除oauth server 端的 Session 
// 注意: wreply=你目前的App想要轉址的網址
header("Location:https://fs.ncku.edu.tw/adfs/ls/?wa=wsignout1.0&wreply=https://xxxx.ncku.edu.tw");
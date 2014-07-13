<?php
/**
 * Zend Framework (http://framework.zend.com/)
 *
 * @link      http://github.com/zendframework/zf2 for the canonical source repository
 * @copyright Copyright (c) 2005-2014 Zend Technologies USA Inc. (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd New BSD License
 */

namespace Zend\EventManager;

use ArrayAccess;

/**
 * Representation of an event
 *
 * Encapsulates the target context and parameters passed, and provides some
 * behavior for interacting with the event manager.
 */
class Event implements EventInterface
{
    /**
     * @var string Event name
     */
    protected $name;

    /**
     * @var string|object The event target
     */
    protected $target;

    /**
     * @var array|ArrayAccess|object The event parameters
     */
    protected $params = array();

    /**
     * @var bool Whether or not to stop propagation
     */
    protected $stopPropagation = false;

    /**
     * Constructor
     *
     * Accept a target and its parameters.
     *
     * @param  string $name Event name
     * @param  string|object $target
     * @param  array|ArrayAccess $params
     */
    public function __construct($name = null, $target = null, $params = null)
    {
        if (null !== $name) {
            $this->setName($name);
        }

        if (null !== $target) {
            $this->setTarget($target);
        }

        if (null !== $params) {
            $this->setParams($params);
        }
    }

    /**
     * Get event name
     *
     * @return string
     */
    public function getName()
    {
        return $this->name;
    }

    /**
     * Get the event target
     *
     * This may be either an object, or the name of a static method.
     *
     * @return string|object
     */
    public function getTarget()
    {
        return $this->target;
    }

    /**
     * Set parameters
     *
     * Overwrites parameters
     *
     * @param  array|ArrayAccess|object $params
     * @return Event
     * @throws Exception\InvalidArgumentException
     */
    public function setParams($params)
    {
        if (!is_array($params) && !is_object($params)) {
            throw new Exception\InvalidArgumentException(sprintf(
                'Event parameters must be an array or object; received "%s"', gettype($params)
            ));
        }

        $this->params = $params;
        return $this;
    }

    /**
     * Get all parameters
     *
     * @return array|object|ArrayAccess
     */
    public function getParams()
    {
        return $this->params;
    }

    /**
     * Get an individual parameter
     *
     * If the parameter does not exist, the $default value will be returned.
     *
     * @param  string|int $name
     * @param  mixed $default
     * @return mixed
     */
    public function getParam($name, $default = null)
    {
        // Check in params that are arrays or implement array access
        if (is_array($this->params) || $this->params instanceof ArrayAccess) {
            if (!isset($this->params[$name])) {
                return $default;
            }

            return $this->params[$name];
        }

        // Check in normal objects
        if (!isset($this->params->{$name})) {
            return $default;
        }
        return $this->params->{$name};
    }

    /**
     * Set the event name
     *
     * @param  string $name
     * @return Event
     */
    public function setName($name)
    {
        $this->name = (string) $name;
        return $this;
    }

    /**
     * Set the event target/context
     *
     * @param  null|string|object $target
     * @return Event
     */
    public function setTarget($target)
    {
        $this->target = $target;
        return $this;
    }

    /**
     * Set an individual parameter to a value
     *
     * @param  string|int $name
     * @param  mixed $value
     * @return Event
     */
    public function setParam($name, $value)
    {
        if (is_array($this->params) || $this->params instanceof ArrayAccess) {
            // Arrays or objects implementing array access
            $this->params[$name] = $value;
        } else {
            // Objects
            $this->params->{$name} = $value;
        }
        return $this;
    }

    /**
     * Stop further event propagation
     *
     * @param  bool $flag
     * @return void
     */
    public function stopPropagation($flag = true)
    {
        $this->stopPropagation = (bool) $flag;
    }

    /**
     * Is propagation stopped?
     *
     * @return bool
     */
    public function propagationIsStopped()
    {
        return $this->stopPropagation;
    }
}
<?php
/**
 * Zend Framework (http://framework.zend.com/)
 *
 * @link      http://github.com/zendframework/zf2 for the canonical source repository
 * @copyright Copyright (c) 2005-2014 Zend Technologies USA Inc. (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd New BSD License
 */

namespace Zend\ProgressBar;

use Zend\Session;

/**
 * Zend\ProgressBar offers an interface for multiple environments.
 */
class ProgressBar
{
    /**
     * Min value
     *
     * @var float
     */
    protected $min;

    /**
     * Max value
     *
     * @var float
     */
    protected $max;

    /**
     * Current value
     *
     * @var float
     */
    protected $current;

    /**
     * Start time of the progressbar, required for ETA
     *
     * @var int
     */
    protected $startTime;

    /**
     * Current status text
     *
     * @var string
     */
    protected $statusText = null;

    /**
     * Adapter for the output
     *
     * @var \Zend\ProgressBar\Adapter\AbstractAdapter
     */
    protected $adapter;

    /**
     * Namespace for keeping the progressbar persistent
     *
     * @var string
     */
    protected $persistenceNamespace = null;

    /**
     * Create a new progressbar backend.
     *
     * @param  Adapter\AbstractAdapter $adapter
     * @param  float|int               $min
     * @param  float|int               $max
     * @param  string|null             $persistenceNamespace
     * @throws Exception\OutOfRangeException When $min is greater than $max
     */
    public function __construct(Adapter\AbstractAdapter $adapter, $min = 0, $max = 100, $persistenceNamespace = null)
    {
        // Check min/max values and set them
        if ($min > $max) {
            throw new Exception\OutOfRangeException('$max must be greater than $min');
        }

        $this->min     = (float) $min;
        $this->max     = (float) $max;
        $this->current = (float) $min;

        // See if we have to open a session namespace
        if ($persistenceNamespace !== null) {
            $this->persistenceNamespace = new Session\Container($persistenceNamespace);
        }

        // Set adapter
        $this->adapter = $adapter;

        // Track the start time
        $this->startTime = time();

        // See If a persistenceNamespace exists and handle accordingly
        if ($this->persistenceNamespace !== null) {
            if (isset($this->persistenceNamespace->isSet)) {
                $this->startTime  = $this->persistenceNamespace->startTime;
                $this->current    = $this->persistenceNamespace->current;
                $this->statusText = $this->persistenceNamespace->statusText;
            } else {
                $this->persistenceNamespace->isSet      = true;
                $this->persistenceNamespace->startTime  = $this->startTime;
                $this->persistenceNamespace->current    = $this->current;
                $this->persistenceNamespace->statusText = $this->statusText;
            }
        } else {
            $this->update();
        }
    }

    /**
     * Get the current adapter
     *
     * @return Adapter\AbstractAdapter
     */
    public function getAdapter()
    {
        return $this->adapter;
    }

    /**
     * Update the progressbar
     *
     * @param  float  $value
     * @param  string $text
     * @return void
     */
    public function update($value = null, $text = null)
    {
        // Update value if given
        if ($value !== null) {
            $this->current = min($this->max, max($this->min, $value));
        }

        // Update text if given
        if ($text !== null) {
            $this->statusText = $text;
        }

        // See if we have to update a namespace
        if ($this->persistenceNamespace !== null) {
            $this->persistenceNamespace->current    = $this->current;
            $this->persistenceNamespace->statusText = $this->statusText;
        }

        // Calculate percent
        if ($this->min === $this->max) {
            $percent = false;
        } else {
            $percent = (float) ($this->current - $this->min) / ($this->max - $this->min);
        }

        // Calculate ETA
        $timeTaken = time() - $this->startTime;

        if ($percent === .0 || $percent === false) {
            $timeRemaining = null;
        } else {
            $timeRemaining = round(((1 / $percent) * $timeTaken) - $timeTaken);
        }

        // Poll the adapter
        $this->adapter->notify($this->current, $this->max, $percent, $timeTaken, $timeRemaining, $this->statusText);
    }

    /**
     * Update the progressbar to the next value
     *
     * @param  int $diff
     * @param  string $text
     * @return void
     */
    public function next($diff = 1, $text = null)
    {
        $this->update(max($this->min, min($this->max, $this->current + $diff)), $text);
    }

    /**
     * Call the adapters finish() behaviour
     *
     * @return void
     */
    public function finish()
    {
        if ($this->persistenceNamespace !== null) {
            unset($this->persistenceNamespace->isSet);
        }

        $this->adapter->finish();
    }
}
<?php
/**
 * Project: Digital Edition Curator
 * File: biz.digitalEditionDayRule.php
 *
 * http://wiki.hearstdigitalnews.com/index.php/Day_Definitions_and_Rules
 *
 * @copyright
 * @author
 */
class digitalEditionDayRule extends businessWcmObject
{
    /**
     * @var int Constant representing that this day would add its associated sections
     */
    const ADDITIVE_OPERATOR = 1;

    /**
     * @var int Constant representing that this day would subtract its associated sections
     */
    const SUBTRACTIVE_OPERATOR = 2;

    /**
     * @var String title
     */
    public $title;

    /**
     * @var Int
     */
    public $siteId;

    /**
     * @var String rule parameters (ex: MONDAY-1-OF-MONTH, LAST-THURSDAY-OF-MONTH, DAY-1-OF-MONTH, TUESDAY)
     */
    public $rule;

    /**
     * @var int 1 = additive, 2 = subtractive. Default is 1.
     */
    public $ruleOperator;

    /**
     * @var String Database Table Name
     */
    protected $tableName = '#__dec_day_rules';


    /**
     * Adds a section definition as a bizrelation to this day rule
     *
     * @param int $id ID of the section definition that we want to add
     *
     * @return boolean Success
     */
    public function addSectionDefinition($id)
    {
        $sDef = new digitalEditionSectionDefinition($id);

        if (!$sDef->id) return false;

        // add a wcmBizrelation to the section
        $relation = new wcmBizrelation();
        $relation->sourceClass = $this->getClass();
        $relation->sourceId = $this->id;
        $relation->destinationClass = $sDef->getClass();
        $relation->destinationId = $sDef->id;
        $relation->kind = wcmBizrelation::IS_COMPOSED_OF;
        $relation->save();

        return true;
    }

    /**
     * Removes a section definition bizrelation from this day rule
     *
     * @param int $id ID of the section definition that we want to subtract
     *
     * @return boolean
     */
    public function removeSectionDefinition($id)
    {
        $sDef = new digitalEditionSectionDefinition($id);

        if (!$sDef->id) return false;

        $br = new wcmBizrelation();

        $sql = 'DELETE FROM ' . $br->getTableName();
        $sql .= ' WHERE sourceClass=? AND sourceId=?';
        $sql .= ' AND destinationClass=? AND destinationId=?';

        $arguments = array(
            $this->getClass(), $this->id,
            $sDef->getClass(), $sDef->id,
        );

        $this->getDatabase()->executeStatement($sql, $arguments);

        return true;
    }

    /**
     * Takes a date and returns the sections that should be added to an edition
     *
     * @param int $siteId
     * @param String $date
     * @param Boolean $liveCreation Whether or not we're creating live-edition specific sections.
     *
     * @return Array
     */
    public function getSectionDefinitionsByDate($siteId, $date, $liveCreation = false)
    {

        $dayRules = $this->getDayRulesForDate($siteId, $date, $liveCreation);

        $sectionsDefinitions = $this->getSectionDefinitionsFromDayRules($dayRules);

        usort($sectionsDefinitions, array('digitalEditionDayRule', 'usortSectionDefinitionsByRank'));

        return $sectionsDefinitions;

    }

    /**
     * Usort comparison function used for sorting section definitions by rank/code
     * If there are equal ranks, we use code. If those are equal, we just count them as matching.
     * This should pretty much never return 0 though.
     *
     * @param digitalEditionSectionDefinition $sDef1
     * @param digitalEditionSectionDefinition $sDef2
     *
     * @return int
     */
    public static function usortSectionDefinitionsByRank($sDef1, $sDef2)
    {
        if ($sDef1->rank == $sDef2->rank) {

            if ($sDef1->code == $sDef2->code) return 0;

            return ($sDef1->code > $sDef2->code) ? +1 : -1;

        }

        return ($sDef1->rank > $sDef2->rank) ? +1 : -1;
    }

    /**
     * Takes an array of day rules and returns an array of sections that should be processed for those day rules
     *
     * @param Array $dayRules
     *
     * @return Array
     */
    private function getSectionDefinitionsFromDayRules($dayRules)
    {

        // Holds the section definition objects that we add
        $sectionDefinitions = array();

        // Stores the ids of the sections that have been added
        $sectionsAdded = array();

        // Stores the ids of the sections that have been subtracted
        $sectionsSubtracted = array();

        // Looping through each dayrule and getting its sections
        foreach ($dayRules as $dr) {

            // Getting the section definitions related to this dayrule
            $sections = self::getDayRuleSectionDefinitions($dr);

            // Looking through all the sections associated with the
            foreach ($sections as $section) {

                // We have to treat additions and subtractions differently (duh)
                switch ($dr->ruleOperator) {

                    case digitalEditionDayRule::ADDITIVE_OPERATOR:
                        // If we haven't already added this section, we add it here
                        if (!in_array($section->id, $sectionsAdded)) {
                            $sectionDefinitions[] = $section;
                            $sectionsAdded[] = $section->id;
                        }
                        break;

                    case digitalEditionDayRule::SUBTRACTIVE_OPERATOR:
                        // If we haven't already added this section to the subtract list, we add it here
                        if (!in_array($section->id, $sectionsSubtracted)) {
                            $sectionsSubtracted[] = $section->id;
                        }
                        break;

                }
            }
        }

        // Removing any subtracted section definitions from our list.
        $processedSectionDefinitions = array();
        foreach($sectionDefinitions as $definition) {
            // If the definition id isn't in the subtracted list, we add it to the final list of sections
            if (!in_array($definition->id, $sectionsSubtracted)) {
                $processedSectionDefinitions[] = $definition;
            }
        }

        return $processedSectionDefinitions;

    }

    /**
     * Accepts a dayRule and returns an array of associated section definitions
     *
     * @param digitalEditionDayRule $dayRule
     *
     * @return Array (digitalEditionSectionDefinition)
     */
    public static function getDayRuleSectionDefinitions($dayRule, $idsOnly = false)
    {
        $br = new wcmBizrelation();
        $sDef = new digitalEditionSectionDefinition();

        $sql = 'SELECT destinationId FROM ' . $br->getTableName();
        $sql .= ' WHERE sourceClass=? AND sourceId=?';
        $sql .= ' AND destinationClass=?';

        $arguments = array(
            $dayRule->getClass(), $dayRule->id,
            $sDef->getClass(),
        );

        $resultSet = $dayRule->getDatabase()->executeQuery($sql, $arguments);

        $sections = array();

        // executeQuery returns null on no rows
        if ($resultSet->getRecordCount() == 0) return $sections;

        while ($resultSet->next()) {
            $row = $resultSet->getRow();
            $sections[] = $idsOnly ? $row['destinationId'] : new digitalEditionSectionDefinition($row['destinationId']);
        }

        return $sections;
    }

    /**
     * Takes our date and gets all the rules that would apply to producing a section for that date
     *
     * @param int $siteId
     * @param String $date
     * @param Boolean $liveCreation Whether or not we're creating live-edition specific sections.
     *
     * @return Array
     */
    private function getDayRulesForDate($siteId, $date, $liveCreation = false)
    {

        $liveAppend = $liveCreation ? '-LIVE' : '';

        $timestamp = strtotime($date);

        // This will hold the list of rules that we need to look up
        $ruleList = array();

        // Getting basic rule check data
        $weekday = strtoupper(date('l', $timestamp));
        $month = strtoupper(date('F', $timestamp));
        $day = date('j', $timestamp);

        // Getting data about the current weekday instance in the month (ex: 2nd Thursday)
        $wiData = $this->getWeekdayInstance($timestamp);


        /**
         * Assembly of rule checking strings
         */

        if ($liveCreation) {
            $ruleList[] = 'LIVE';
        }

        // Every day!
        $ruleList[] = 'EVERYDAY'.$liveAppend;

        // Checking the simple weekday
        $ruleList[] = $weekday.$liveAppend;

        // Checking the day of the month
        $ruleList[] = 'DAY-'.$day.'-OF-MONTH'.$liveAppend;

        // Checking the specific day of THIS month
        $ruleList[] = 'DAY-'.$day.'-OF-'.$month.$liveAppend;

        // Adding a rule for this weekday instance (THURSDAY-4-OF-MONTH)
        $ruleList[] = $weekday.'-'.$wiData['instance'].'-OF-MONTH'.$liveAppend;

        // Seeing if this is the first weekday instance of this type per month
        if ($wiData['instance'] === 1) {
            $ruleList[] = 'FIRST-'.$weekday.'-OF-MONTH'.$liveAppend;
        }

        // Seeing if this is the first weekday instance of this type per month
        if ($wiData['instance'] === $wiData['total']) {
            $ruleList[] = 'LAST-'.$weekday.'-OF-MONTH'.$liveAppend;
        }

        // Seeing if this is the first day of the month
        if ($day == 1) {
            $ruleList[] = 'FIRST-DAY-OF-MONTH'.$liveAppend;
        }

        // Seeing if this is the last day of the month. (seeing if tomorrow is a member of a different month)
        if (strtoupper(date('F', $timestamp+86400)) !== $month) {
            $ruleList[] = 'LAST-DAY-OF-MONTH'.$liveAppend;
        }


        /**
         * Getting all the day rules that apply to the rule checks we generated
         */

        $where = "rule IN ('".  implode("','", $ruleList)."') AND siteId='".$siteId."'";

        $rulesToProcess = array();

        $enum = new digitalEditionDayRule();
        $enum->beginEnum($where, 'ruleOperator ASC');

        while ($enum->nextEnum()) {
            $rulesToProcess[] = clone $enum;
        }

        return $rulesToProcess;

    }

    /**
     * Takes a date and returns an array of: The current instance of a weekday in
     * the month, and the total number of instances of that weekday in the month.
     *
     * @param int $date
     *
     * @return Array instance, total
     */
    private function getWeekdayInstance($timestamp)
    {
        // weekday instance, total possible weekday instances
        $instanceArray = array(
            'instance' => 0,
            'total' => 0,
        );

        $secondsPerWeek = 604800;

        $month = date('n', $timestamp);


        // Getting what weekday instance of the month it is
        $workstamp = $timestamp;

        while (date('n', $workstamp) === $month) {
            // We increment the total as well as just the instance we're looking at
            $instanceArray['instance']++;
            $instanceArray['total']++;

            // Looking at last week.
            $workstamp -= $secondsPerWeek;
        }


        // Seeing how many weekdays of this type there are in this month
        $workstamp = $timestamp + $secondsPerWeek;

        while (date('n', $workstamp) === $month) {
            // Adding this iteration to the total
            $instanceArray['total']++;

            // Looking at last week.
            $workstamp += $secondsPerWeek;
        }

        return $instanceArray;
    }

}

<?php
/**
 * BackPress script procedural API.
 *
 * @package BackPress
 * @since r16
 */

/**
 * Prints script tags in document head.
 *
 * Called by admin-header.php and by wp_head hook. Since it is called by wp_head
 * on every page load, the function does not instantiate the WP_Scripts object
 * unless script names are explicitly passed. Does make use of already
 * instantiated $wp_scripts if present. Use provided wp_print_scripts hook to
 * register/enqueue new scripts.
 *
 * @since r16
 * @see WP_Dependencies::print_scripts()
 */
function wp_print_scripts( $handles = false ) {
    do_action( 'wp_print_scripts' );
    if ( '' === $handles ) // for wp_head
        $handles = false;

    global $wp_scripts;
    if ( ! is_a( $wp_scripts, 'WP_Scripts' ) ) {
        if ( ! did_action( 'init' ) )
            _doing_it_wrong( __FUNCTION__, sprintf( __( 'Scripts and styles should not be registered or enqueued until the %1$s, %2$s, or %3$s hooks.' ),
                '<code>wp_enqueue_scripts</code>', '<code>admin_enqueue_scripts</code>', '<code>init</code>' ), '3.3' );

        if ( !$handles )
            return array(); // No need to instantiate if nothing is there.
        else
            $wp_scripts = new WP_Scripts();
    }

    return $wp_scripts->do_items( $handles );
}

/**
 * Register new Javascript file.
 *
 * @since r16
 * @param string $handle Script name
 * @param string $src Script url
 * @param array $deps (optional) Array of script names on which this script depends
 * @param string|bool $ver (optional) Script version (used for cache busting), set to null to disable
 * @param bool $in_footer (optional) Whether to enqueue the script before </head> or before </body>
 * @return null
 */
function wp_register_script( $handle, $src, $deps = array(), $ver = false, $in_footer = false ) {
    global $wp_scripts;
    if ( ! is_a( $wp_scripts, 'WP_Scripts' ) ) {
        if ( ! did_action( 'init' ) )
            _doing_it_wrong( __FUNCTION__, sprintf( __( 'Scripts and styles should not be registered or enqueued until the %1$s, %2$s, or %3$s hooks.' ),
                '<code>wp_enqueue_scripts</code>', '<code>admin_enqueue_scripts</code>', '<code>init</code>' ), '3.3' );
        $wp_scripts = new WP_Scripts();
    }

    $wp_scripts->add( $handle, $src, $deps, $ver );
    if ( $in_footer )
        $wp_scripts->add_data( $handle, 'group', 1 );
}

/**
 * Wrapper for $wp_scripts->localize().
 *
 * Used to localizes a script.
 * Works only if the script has already been added.
 * Accepts an associative array $l10n and creates JS object:
 * "$object_name" = {
 *   key: value,
 *   key: value,
 *   ...
 * }
 * See http://core.trac.wordpress.org/ticket/11520 for more information.
 *
 * @since r16
 *
 * @param string $handle The script handle that was registered or used in script-loader
 * @param string $object_name Name for the created JS object. This is passed directly so it should be qualified JS variable /[a-zA-Z0-9_]+/
 * @param array $l10n Associative PHP array containing the translated strings. HTML entities will be converted and the array will be JSON encoded.
 * @return bool Whether the localization was added successfully.
 */
function wp_localize_script( $handle, $object_name, $l10n ) {
    global $wp_scripts;
    if ( ! is_a( $wp_scripts, 'WP_Scripts' ) ) {
        if ( ! did_action( 'init' ) )
            _doing_it_wrong( __FUNCTION__, sprintf( __( 'Scripts and styles should not be registered or enqueued until the %1$s, %2$s, or %3$s hooks.' ),
                '<code>wp_enqueue_scripts</code>', '<code>admin_enqueue_scripts</code>', '<code>init</code>' ), '3.3' );

        return false;
    }

    return $wp_scripts->localize( $handle, $object_name, $l10n );
}

/**
 * Remove a registered script.
 *
 * @since r16
 * @see WP_Scripts::remove() For parameter information.
 */
function wp_deregister_script( $handle ) {
    global $wp_scripts;
    if ( ! is_a( $wp_scripts, 'WP_Scripts' ) ) {
        if ( ! did_action( 'init' ) )
            _doing_it_wrong( __FUNCTION__, sprintf( __( 'Scripts and styles should not be registered or enqueued until the %1$s, %2$s, or %3$s hooks.' ),
                '<code>wp_enqueue_scripts</code>', '<code>admin_enqueue_scripts</code>', '<code>init</code>' ), '3.3' );
        $wp_scripts = new WP_Scripts();
    }

    $wp_scripts->remove( $handle );
}

/**
 * Enqueues script.
 *
 * Registers the script if src provided (does NOT overwrite) and enqueues.
 *
 * @since r16
 * @see wp_register_script() For parameter information.
 */
function wp_enqueue_script( $handle, $src = false, $deps = array(), $ver = false, $in_footer = false ) {
    global $wp_scripts;
    if ( ! is_a( $wp_scripts, 'WP_Scripts' ) ) {
        if ( ! did_action( 'init' ) )
            _doing_it_wrong( __FUNCTION__, sprintf( __( 'Scripts and styles should not be registered or enqueued until the %1$s, %2$s, or %3$s hooks.' ),
                '<code>wp_enqueue_scripts</code>', '<code>admin_enqueue_scripts</code>', '<code>init</code>' ), '3.3' );
        $wp_scripts = new WP_Scripts();
    }

    if ( $src ) {
        $_handle = explode('?', $handle);
        $wp_scripts->add( $_handle[0], $src, $deps, $ver );
        if ( $in_footer )
            $wp_scripts->add_data( $_handle[0], 'group', 1 );
    }
    $wp_scripts->enqueue( $handle );
}

/**
 * Remove an enqueued script.
 *
 * @since WP 3.1
 * @see WP_Scripts::dequeue() For parameter information.
 */
function wp_dequeue_script( $handle ) {
    global $wp_scripts;
    if ( ! is_a( $wp_scripts, 'WP_Scripts' ) ) {
        if ( ! did_action( 'init' ) )
            _doing_it_wrong( __FUNCTION__, sprintf( __( 'Scripts and styles should not be registered or enqueued until the %1$s, %2$s, or %3$s hooks.' ),
                '<code>wp_enqueue_scripts</code>', '<code>admin_enqueue_scripts</code>', '<code>init</code>' ), '3.3' );
        $wp_scripts = new WP_Scripts();
    }

    $wp_scripts->dequeue( $handle );
}

/**
 * Check whether script has been added to WordPress Scripts.
 *
 * The values for list defaults to 'queue', which is the same as enqueue for
 * scripts.
 *
 * @since WP unknown; BP unknown
 *
 * @param string $handle Handle used to add script.
 * @param string $list Optional, defaults to 'queue'. Others values are 'registered', 'queue', 'done', 'to_do'
 * @return bool
 */
function wp_script_is( $handle, $list = 'queue' ) {
    global $wp_scripts;
    if ( ! is_a( $wp_scripts, 'WP_Scripts' ) ) {
        if ( ! did_action( 'init' ) )
            _doing_it_wrong( __FUNCTION__, sprintf( __( 'Scripts and styles should not be registered or enqueued until the %1$s, %2$s, or %3$s hooks.' ),
                '<code>wp_enqueue_scripts</code>', '<code>admin_enqueue_scripts</code>', '<code>init</code>' ), '3.3' );
        $wp_scripts = new WP_Scripts();
    }

    $query = $wp_scripts->query( $handle, $list );

    if ( is_object( $query ) )
        return true;

    return $query;
}

<?php
/**
*
* @package build
* @copyright (c) 2010 phpBB Group
* @license http://opensource.org/licenses/gpl-2.0.php GNU General Public License v2
*
*/

class build_package
{
    var $package_infos;
    var $old_packages;
    var $versions;
    var $locations;

    // -c - context diff
    // -r - compare recursive
    // -N - Treat missing files as empty
    // -E - Ignore tab expansions
    //      not used: -b - Ignore space changes.
    // -w - Ignore all whitespace
    // -B - Ignore blank lines
    // -d - Try to find smaller set of changes
    var $diff_options = '-crNEBwd';
    var $diff_options_long = '-x images -crNEB'; // -x fonts -x imageset //imageset not used here, because it includes the imageset.cfg file. ;)

    var $verbose = false;
    var $status_begun = false;
    var $num_dots = 0;

    function build_package($versions, $verbose = false)
    {
        $this->versions = $versions;
        $this->verbose = $verbose;

        // Get last two entries
        $_latest = $this->versions[sizeof($this->versions) - 1];
        $_before = $this->versions[sizeof($this->versions) - 2];

        $this->locations = array(
            'new_version'   => dirname(dirname(__FILE__)) . '/phpBB/',
            'old_versions'  => dirname(__FILE__) . '/old_versions/',
            'root'          => dirname(__FILE__) . '/',
            'package_dir'   => dirname(__FILE__) . '/new_version/'
        );

        $this->package_infos = array(
            'package_name'          => 'phpBB3',
            'name_prefix'           => 'phpbb',
            'simple_name'           => 'release-' . $_latest,
            'new_version_number'    => $_latest,
            'short_version_number'  => str_replace('.', '', $_latest),
            'release_filename'      => 'phpBB-' . $_latest,
            'last_version'          => 'release-' . $_before,
            'last_version_number'   => $_before,
        );

        $this->package_infos['dest_dir'] = $this->locations['package_dir'] . $this->package_infos['package_name'];
        $this->package_infos['diff_dir'] = $this->locations['old_versions'] . $this->package_infos['simple_name'];
        $this->package_infos['patch_directory'] = $this->locations['package_dir'] . 'patches';
        $this->package_infos['files_directory'] = $this->locations['package_dir'] . 'files';
        $this->package_infos['update_directory'] = $this->locations['package_dir'] . 'update';
        $this->package_infos['release_directory'] = $this->locations['package_dir'] . 'release_files';

        // Old packages always exclude the latest version. ;)
        $this->old_packages = array();

        foreach ($this->versions as $package_version)
        {
            if ($package_version == $_latest)
            {
                continue;
            }

            $this->old_packages['release-' . $package_version] = $package_version . '_to_';
        }
    }

    function get($var)
    {
        return $this->package_infos[$var];
    }

    function begin_status($headline)
    {
        if ($this->status_begun)
        {
            echo "\nDone.\n\n";
        }

        $this->num_dots = 0;

        echo $headline . "\n    ";

        $this->status_begun = true;
    }

    function run_command($command)
    {
        $result = trim(`$command`);

        if ($this->verbose)
        {
            echo "    command : " . getcwd() . '$ ' . $command . "\n";
            echo "    result  : " . $result . "\n";
        }
        else
        {
            if ($this->num_dots > 70)
            {
                echo "\n";
                $this->num_dots = 0;
            }
            echo '.';
            $this->num_dots++;
        }

        flush();
    }

    function create_directory($directory, $dir_struct)
    {
        if (!file_exists($directory))
        {
            $this->run_command("mkdir $directory");
        }

        if (is_array($dir_struct))
        {
            foreach ($dir_struct as $_dir => $_dir_struct)
            {
                $this->create_directory($directory . '/' . $_dir, $_dir_struct);
            }
        }
    }

    function collect_diff_files($diff_filename, $package_name)
    {
        $diff_result = $binary = array();
        $diff_contents = file($diff_filename);

        $special_diff_contents = array();

        foreach ($diff_contents as $num => $line)
        {
            $line = trim($line);

            if (!$line)
            {
                continue;
            }

            // Special diff content?
            if (strpos($line, 'diff ' . $this->diff_options . ' ') === 0 || strpos($line, '*** ') === 0 || strpos($line, '--- ') === 0 || (strpos($line, ' Exp $') !== false && strpos($line, '$Id:') !== false))
            {
                $special_diff_contents[] = $line;
            }
            else if (strpos($line, 'diff ' . $this->diff_options . ' ') === 0 || strpos($line, '*** ') === 0 || strpos($line, '--- ') === 0 || (strpos($line, ' Exp $') !== false && strpos($line, '$Id:') !== false) || (strpos($line, ' $') !== false && strpos($line, '$Id:') !== false))
            {
                $special_diff_contents[] = $line;
            }

            // Is diffing line?
            if (strstr($line, 'diff ' . $this->diff_options . ' '))
            {
                $next_line = $diff_contents[$num+1];
                if (strpos($next_line, '***') === 0)
                {
    //          *** phpbb208/admin/admin_board.php  Sat Jul 10 20:16:26 2004
                    $next_line = explode("\t", $next_line);
                    $next_line = trim($next_line[0]);
                    $next_line = str_replace('*** ' . $package_name . '/', '', $next_line);
                    $diff_result[] = $next_line;
                }
            }

            // Is binary?
            if (preg_match('/^Binary files ' . $package_name . '\/(.*) and [a-z0-9._-]+\/\1 differ/i', $line, $match))
            {
                $binary[] = trim($match[1]);
            }
        }

        // Now go through the list again and find out which files have how many changes...
        $num_changes = array();

    /*  [1070] => diff -crN phpbb200/includes/usercp_avatar.php phpbb2023/includes/usercp_avatar.php
        [1071] => *** phpbb200/includes/usercp_avatar.php   Sat Jul 10 20:16:13 2004
        [1072] => --- phpbb2023/includes/usercp_avatar.php  Wed Feb  6 22:28:04 2008
        [1073] => *** 6,12 ****
        [1074] => !  *   $Id$
        [1075] => --- 6,12 ----
        [1076] => *** 51,59 ****
        [1077] => --- 51,60 ----
        [1078] => *** 62,80 ****
        [1079] => --- 63,108 ----
        [1080] => *** 87,97 ****
    */
        while (($line = array_shift($special_diff_contents)) !== NULL)
        {
            $line = trim($line);

            if (!$line)
            {
                continue;
            }

            // Is diffing line?
            if (strstr($line, 'diff ' . $this->diff_options . ' '))
            {
                $next_line = array_shift($special_diff_contents);
                if (strpos($next_line, '*** ') === 0)
                {
    //          *** phpbb208/admin/admin_board.php  Sat Jul 10 20:16:26 2004
                    $next_line = explode("\t", $next_line);
                    $next_line = trim($next_line[0]);
                    $next_line = str_replace('*** ' . $package_name . '/', '', $next_line);

                    $is_reached = false;
                    $prev_line = '';

                    while (!$is_reached)
                    {
                        $line = array_shift($special_diff_contents);

                        if (strpos($line, 'diff ' . $this->diff_options) === 0 || empty($special_diff_contents))
                        {
                            $is_reached = true;
                            array_unshift($special_diff_contents, $line);
                            continue;
                        }

                        if (strpos($line, '*** ') === 0 && strpos($line, ' ****') !== false)
                        {
                            $is_comment = false;
                            while (!(strpos($line, '--- ') === 0 && strpos($line, ' ----') !== false))
                            {
                                $line = array_shift($special_diff_contents);
                                if (strpos($line, ' Exp $') !== false || strpos($line, '$Id:') !== false)
                                {
                                    $is_comment = true;
                                }
                            }

                            if (!$is_comment)
                            {
                                if (!isset($num_changes[$next_line]))
                                {
                                    $num_changes[$next_line] = 1;
                                }
                                else
                                {
                                    $num_changes[$next_line]++;
                                }
                            }
                        }
                    }
                }
            }
        }

        // Now remove those results not having changes
        $return = array();

        foreach ($diff_result as $key => $value)
        {
            if (isset($num_changes[$value]))
            {
                $return[] = $value;
            }
        }

        foreach ($binary as $value)
        {
            $return[] = $value;
        }

        $diff_result = $return;
        unset($return);
        unset($special_diff_contents);

        $result = array(
            'files'     => array(),
            'binary'    => array(),
            'all'       => $diff_result,
        );

        $binary_extensions = array('gif', 'jpg', 'jpeg', 'png', 'ttf');

        // Split into file and binary
        foreach ($diff_result as $filename)
        {
            if (strpos($filename, '.') === false)
            {
                $result['files'][] = $filename;
                continue;
            }

            $extension = explode('.', $filename);
            $extension = array_pop($extension);

            if (in_array($extension, $binary_extensions))
            {
                $result['binary'][] = $filename;
            }
            else
            {
                $result['files'][] = $filename;
            }
        }

        return $result;
    }
}

<?php
    /*
        File Path:      /system/ci/system/amfphp/services/LaunchRPC.php
        Comments:
            This file is an amfphp rpc server.
    */
    
    //----------------------------------------------------------------------------------------------------
    // CI MODEL OPENER START
    
    // This will store all the global config data for LaunchCMS.  One var to rule them all!  (And not pollute the global namespace too much)
    global $LAUNCH;
    $LAUNCH = array();
    $LAUNCH["paths"] = array();
    
    // Initial "root" directory setup
    $arrLaunchRoot = explode("system/amfphp", dirname(__FILE__));
    $LAUNCH["paths"]["launch"] = $arrLaunchRoot[0];
    
    // Setting up the current launchcms/ root URL; domain and all
    $arrCurrentDir = explode("system/amfphp", dirname($_SERVER["PHP_SELF"]));
    $strCurrentDir = $arrCurrentDir[0];
    if ( $strCurrentDir{strlen($strCurrentDir) - 1} == "/" ) $strCurrentDir = substr($strCurrentDir, 0, -1);
    if ( isset($_SERVER['HTTPS']) ) $LAUNCH["root_url"] = 'https://' . $_SERVER['HTTP_HOST'] . $strCurrentDir."/";
    else $LAUNCH["root_url"] = 'http://' . $_SERVER['HTTP_HOST'] . $strCurrentDir."/";
    
    // This file contains global variables to all our paths.
    require_once($LAUNCH["paths"]["launch"]."config/paths.php");
    
    // These file allows us to access CI models without having to go through CI
    require_once($LAUNCH["paths"]["cimodel"].'ci_model_remote_open.php');
    
    // CI MODEL OPENER END
    //----------------------------------------------------------------------------------------------------



    // Create new service for PHP Remoting as Class
    // Extends LaunchCMS because it gives us access to all CI libraries as well as our DB model
    class LaunchRPC extends LaunchCMS {
    
    
        // If they fail authentication, we're going to send this back as a result
        var $arrBadAuth = array();
        
        
        function LaunchRPC () {

            // Calling the LaunchCMS constructor which calls the Model constructor...etc...
            parent::LaunchCMS();
            
            // Setting up our response to a bad authentication
            $this->arrBadAuth[0]->auth = "FALSE";
            
            // Define the methodTable for this class in the constructor
            $this->methodTable  =   array(
            
                "adminLogin"        =>  array(  "description"   =>  "Return auth information if they're legit",
                                                "access"        =>  "remote"),
                "getAdminSession"   =>  array(  "description"   =>  "Checked if there is a session or cookie set for the users login information and returns it",
                                                "access"        =>  "remote"),
                "adminLogout"       =>  array(  "description"   =>  "Logs the admin user out and removes all the session/cookie information for their account",
                                                "access"        =>  "remote"),
                "dbDelete"          =>  array(  "description"   =>  "Deletes data in the DB",
                                                "access"        =>  "remote"),
                "dbInsert"          =>  array(  "description"   =>  "Inserts information into the DB",
                                                "access"        =>  "remote"),
                "dbSelect"          =>  array(  "description"   =>  "Returns general information to the admin panel",
                                                "access"        =>  "remote"),
                "dbUpdate"          =>  array(  "description"   =>  "Updates data in the DB",
                                                "access"        =>  "remote"),
                "getLang"           =>  array(  "description"   =>  "Retrives the language preference from the DB",
                                                "access"        =>  "remote"),
                "getDirListing"     =>  array(  "description"   =>  "Retrives the directory listing from filestore",
                                                "access"        =>  "remote"),
                "getCustomListing"  =>  array(  "description"   =>  "Gets a custom passed in directory listing based on the launch root.",
                                                "access"        =>  "remote"),
                "getThemeListing"   =>  array(  "description"   =>  "Retrives the directory listing for the themes directory",
                                                "access"        =>  "remote"),
                "getLoginLogoURL"   =>  array(  "description"   =>  "Gets the URL of the login logo",
                                                "access"        =>  "remote"),
                "createDir"         =>  array(  "description"   =>  "Creates a directory",
                                                "access"        =>  "remote"),
                "moveToTrash"       =>  array(  "description"   =>  "Moves a file or folder to the trash can",
                                                "access"        =>  "remote"),
                "moveFileOrFolder"  =>  array(  "description"   =>  "Moves a file or folder another folder",
                                                "access"        =>  "remote"),
                "deleteFileOrFolder"=>  array(  "description"   =>  "Deletes a file or folder",
                                                "access"        =>  "remote"),
                "renameFileOrFolder"=>  array(  "description"   =>  "Renames a file or folder",
                                                "access"        =>  "remote"),
                "emptyTrash"        =>  array(  "description"   =>  "Empties the current users trash",
                                                "access"        =>  "remote"),
                "phpSettings"       =>  array(  "description"   =>  "Returns a list of pre-defined php settings",
                                                "access"        =>  "remote"),
                "getPluginListing"  =>  array(  "description"   =>  "Returns a listing of the contents of the plugins directory",
                                                "access"        =>  "remote"),
                "changePluginStatus"=>  array(  "description"   =>  "enables/installs or disabled a plugin",
                                                "access"        =>  "remote")
                                        );
            
        }
        
        
        
        // This function will see if the user already has a session or cookie data with login information
        function getAdminSession() {
            
            // Starting the session if it's not started yet.
            if ( !isset($_SESSION) ) session_start();
            
            // Getting the username and authstring if it's set, returning false if not
            if ( isset($_SESSION["auth_data"]["un"]) && isset($_SESSION["auth_data"]["as"]) ) {
                $strUserName = $_SESSION["auth_data"]["un"];
                $strAuthString = $_SESSION["auth_data"]["as"];
            }
            else {
                // Loading the cookie helper so we can check for auth cookies
                $this->load->helper('cookie');
                
                if ( get_cookie("un") && get_cookie("as") ) {
                    $strUserName = get_cookie("un");
                    $strAuthString = get_cookie("as");
                }
                else return false;
            }
            
            // Seeing if the user is authorized to login here
            $objUserData = $this->authUser($strUserName, $strAuthString, true);
            
            // If the returned auth information is false, returning false
            if ( !$objUserData ) return false;
            
            // The user was authorized, getting their information
            $objReturnAuth = $this->getSecurityData($objUserData);
            $objReturnAuth = $this->getUserData($objReturnAuth);
            $this->getBackgroundInfo($objReturnAuth);
            $this->getURLInfo($objReturnAuth);
            $objReturnAuth->auth_string = $strAuthString;
            
            return $objReturnAuth;
        
        }
        
    
        
        // This function logs admins in
        function adminLogin($arrLogin) {
            
            $objLoginData = $this->loginUser($arrLogin[0], $arrLogin[1], true);
            
            if ( !$objLoginData ) return false;
        
            // Getting the user's background preferences
            $this->getBackgroundInfo($objLoginData);
            
            // Starting the session if it's not started yet.
            if ( !isset($_SESSION) ) session_start();
            
            
            // Saving the login information in a session
            $_SESSION["auth_data"] = array();
            $_SESSION["auth_data"]["un"] = $objLoginData->username;
            $_SESSION["auth_data"]["as"] = $objLoginData->auth_string;
            
            
            // $arrLogin[2] is a boolean which sets "remember me" or not
            // If they want to be remembered, we save a cookie
            if ( isset($arrLogin[2]) && $arrLogin[2] == true ) {
                // Loading the cookie helper
                $this->load->helper('cookie');
                
                $unCookie = array( 'name' => 'un', 'value' => $varAuth[0]->username, 'expire' => '31556926' );
                set_cookie($unCookie);
                
                $asCookie = array( 'name' => 'as', 'value' => $varAuth[0]->auth_string, 'expire' => '31556926' );
                set_cookie($asCookie);
                
                $objLoginData->cookie = "set";
            }
            
            // Returning login information.  
            return $objLoginData;
            
        }
        
        
        
        // This function will setup/get the interface background information that the user has set
        function getBackgroundInfo( &$objLoginData ) {
        
            // Setting up a db query to pull in the background information the user has specified
            $this->db->select("name, value");
            $this->db->from("settings_users");
            $this->db->where("app = 'base' AND users_id = '".$objLoginData->users_id."' AND (name = 'background_img' OR name = 'background_grad')");
            $arrBGInfo = $this->select();
            
            // if there was an item set for the background type and for the background itself, we want to pull out the values and return them
            if ( count($arrBGInfo) > 0 ) {
                // Looping through all the returned values and setting the type and background
                for ( $i = 0 ; $i < count($arrBGInfo); $i++ ) {
                    if ( $arrBGInfo[$i]->name == "background_grad" ) {
                        $objLoginData->background_grad = $arrBGInfo[$i]->value;
                    }
                    elseif ( $arrBGInfo[$i]->name == "background_img" ) {
                        $objLoginData->background_img = $arrBGInfo[$i]->value;
                    }
                }
            }
            // There were no rows in the DB containing the background image data
            else {
                // Inserting the background gradient data
                $data = array(
                   'users_id' => $objLoginData->users_id,
                   'name' => 'background_grad',
                   'value' => '3368601|3394815',
                   'app' => 'base'
                );
                $this->db->insert('settings_users', $data);
                // Inserting the background image data
                $data = array(
                   'users_id' => $objLoginData->users_id,
                   'name' => 'background_img',
                   'value' => '',
                   'app' => 'base'
                );
                $this->db->insert('settings_users', $data);
                
                // Setting the background information that we'll be returning
                $objLoginData->background_img = "";
                $objLoginData->background_grad = "3368601|3394815";
            }
        
        }
        
        
        
        // This will get the URL and root-url and pass them back.
        function getURLInfo( &$objLoginData ) {
        
            global $LAUNCH;
        
            
            $objLoginData->root_url = $LAUNCH["root_url"];
            $objLoginData->url = $LAUNCH["root_url"] . "?l=";
            
            // Defaulting clean urls to false
            $boolCleanURLS = false;
                
            if ( in_array("mod_rewrite", apache_get_modules()) ) {
            
                // Checking for the .htaccess file
                if ( file_exists($LAUNCH["paths"]["launch"].".htaccess") ) {
                    
                    // If we find our 'index.php?l=' that's reason enough to believe they've put the correct .htaccess file together
                    if ( strstr(file_get_contents($LAUNCH["paths"]["launch"].".htaccess"), "index.php?l=") ) {
                        $boolCleanURLS = true;
                    }
                }
            }
                
            // If clean urls are NOT enabled, we want to append the location string "?l=" to the end of the root URL.
            $objLoginData->url = $LAUNCH["root_url"];
            if ( !$boolCleanURLS ) $objLoginData->url .= "?l=";
            
        }
        
        
        
        
        // Logs the admin user out and removes all the session/cookie information for their account
        function adminLogout($arrAuthInfo) {
            
            if ( !$this->authUser($arrAuthInfo[0], $arrAuthInfo[1], true) ) return false;
            
            // Starting the session if it's not started yet.
            if ( !isset($_SESSION) ) session_start();
            
            // Loading the cookie helper
            $this->load->helper('cookie');
            
            // Clearing all sessions and cookies having to do with the user's login
            $_SESSION["auth_data"] = array();
            delete_cookie("un");
            delete_cookie("as");
            
            return true;
            
        }
        
        
        
        
        
        // This is for deleting data from the DB
        function dbDelete($arrParams) {
        
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
                
                $arrResult = array();
            
                if ( $this->delete($arrParams[2], $arrParams[3]) ) {
                    $arrResult[0]->success = "TRUE";
                    return $arrResult;
                }
                else {
                    $arrResult[0]->success = "FALSE";
                    return $arrResult;
                }
                
            } else return $this->arrBadAuth;
        
        }
        
        
        
        // This is for general insertion of data
        function dbInsert($arrParams) {
        
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                $arrInsertParams = array();
                
                // Setting up the array of parameters to be inserted
                for ( $i = 0; $i < count($arrParams[3][0]); $i++ ) {
                    
                    // Setting the element name and value to the values of the elements of their array
                    $this->db->set($arrParams[3][0][$i], $arrParams[3][1][$i]);
                    
                }

                $arrResult = array();
            
                if ( $this->db->insert($arrParams[2]) ) {
                    
                    // We want to set and return the ID of the new record we just added if $arrParams[4] is set
                    if ( isset($arrParams[4]) && $arrParams[4] != "" ) {
                        $this->db->select($arrParams[4]);
                        $this->db->from($arrParams[2]);
                        $this->db->limit(1);
                        $this->db->orderby($arrParams[4], "desc");
                        $arrIDResult = $this->select(null);
                        $arrResult[0]->newID = $arrIDResult[0]->$arrParams[4];
                    }
                    
                    $arrResult[0]->success = "TRUE";
                    return $arrResult;
                    
                }
                else {
                    $arrResult[0]->success = "FALSE";
                    return $arrResult;
                }
            
            } else return $this->arrBadAuth;
        
        }
        
        
        
        // This is for general selection and returning of values.
        function dbSelect($arrParams) {
        
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
                
                // Removing the user name and auth string since we don't need them anymore
                // the $this->select() function doesn't like them either ;)
                array_shift($arrParams);
                array_shift($arrParams);
                
                return $this->select($arrParams);
                
            } else return $this->arrBadAuth;
            
        }
        
        
        
        // This is for updating information in the database
        function dbUpdate($arrParams) {
        
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                $arrInsertParams = array();
                
                // Setting up the array of parameters to be updated
                for ( $i = 0; $i < count($arrParams[3][0]); $i++ ) {
                    
                    // Setting the element name and value to the values of the elements of their array
                    $this->db->set($arrParams[3][0][$i], $arrParams[3][1][$i]);
                    
                }
                
                $arrResult = array();
                
                $this->db->where($arrParams[4]);
            
                if ( $this->db->update($arrParams[2]) ) {
                    $arrResult[0]->success = "TRUE";
                    return $arrResult;
                }
                else {
                    $arrResult[0]->success = "FALSE";
                    return $arrResult;
                }
            
            } else return $this->arrBadAuth;
            
        }
        
        
        
        // This will return the language preference set up in the base DB table
        function getLang() {
        
            // Setting up the db query
            $this->db->select("value");
            $this->db->from("settings_global");
            $this->db->where("name", "language");
            $this->db->where("app", "base");
            
            // Getting the information from the DB.
            $arrDefaultLanguage = $this->select(null);
    
            return $arrDefaultLanguage[0]->value;
        
        }
        
        
        // Returns the path to the login logo url
        function getLoginLogoURL() {
        
            // Setting up the db query
            $this->db->select("value");
            $this->db->from("settings_global");
            $this->db->where("name", "login_logo_url");
            $this->db->where("app", "base");
            
            // Getting the information from the DB.
            $arrDefaultLanguage = $this->select();
    
            return $arrDefaultLanguage[0]->value;
                    
        }
        
        
        
        // This will return an object full of php settings that we want to send back
        function phpSettings($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                // Getting the max upload file size and max post size and replacing M/K with their integer values
                $umf = str_replace("K", "000", str_replace("M", "000000", ini_get('upload_max_filesize')));
                $pms = str_replace("K", "000", str_replace("M", "000000", ini_get('post_max_size')));
                // Saving the smaller of the two because this is the small-limit on a file-upload size
                if ( $umf < $pms ) $objResponse->intMaxFileSize = $umf;
                else $objResponse->intMaxFileSize = $pms;
                
                $sm = ini_get('safe_mode');
                if ( $sm == "0" || strtolower($sm) == "off" ) $objResponse->boolSafeMode = false;
                else $objResponse->boolSafeMode = true;
                
                return $objResponse;
                
            } else return $this->arrBadAuth;
        }
        
        
        
        
        
        /*-------------------------------------------------------//
        //-- THESE FUNCTIONS ARE FOR FILE/DIRECTORY OPERATIONS --//
        //-------------------------------------------------------*/
        
        
        // This function will retrieve a directory listing from the filestore folder
        function getDirListing($arrParams) {
        
            if ( !$this->authUser($arrParams[0], $arrParams[1], true) ) return $this->arrBadAuth;
                
            global $LAUNCH;
            
            // Creating the main user directory if it doesn't exist, and filling it with optional directories
            if ( !is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]) ) {
                mkdir($LAUNCH["paths"]["userfiles"].$arrParams[0], 0777);
                // the mkdir doesn't always properly set the permissions to 0777 so we're gonna chmod it ourselves
                chmod($LAUNCH["paths"]["userfiles"].$arrParams[0], 0777);
            }
            
            // Making sure the main two folders exists inside the USER'S folder
            $arrUserDirs = array("default","home");
            for ( $i = 0; $i < count($arrUserDirs); $i++ ) {
                if ( !is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/".$arrUserDirs[$i]) ) {
                    mkdir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/".$arrUserDirs[$i], 0777);
                    chmod($LAUNCH["paths"]["userfiles"].$arrParams[0]."/".$arrUserDirs[$i], 0777);
                }
            }
            
            // Making sure the required two folders exists inside the USER'S DEFAULT folder
            $arrDefaultUserDirs = array("Desktop","Trash");
            for ( $i = 0; $i < count($arrDefaultUserDirs); $i++ ) {
                if ( !is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/".$arrDefaultUserDirs[$i]) ) {
                    mkdir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/".$arrDefaultUserDirs[$i], 0777);
                    chmod($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/".$arrDefaultUserDirs[$i], 0777);
                }
            }
            
            // Making sure the main four folders exists inside the SHARE folder
            $arrInternalShareDirs = array("Documents","Images","Audio-Video","Library");
            for ( $i = 0; $i < count($arrInternalShareDirs); $i++ ) {
                if ( !is_dir($LAUNCH["paths"]["share"].$arrInternalShareDirs[$i]) ) {
                    mkdir($LAUNCH["paths"]["share"].$arrInternalShareDirs[$i], 0777);
                    chmod($LAUNCH["paths"]["share"].$arrInternalShareDirs[$i], 0777);
                }
            }
            
            // Making sure the Backgrounds folder exists in the images folder
            if ( !is_dir($LAUNCH["paths"]["share"]."Images/Backgrounds") ) {
                mkdir($LAUNCH["paths"]["share"]."Images/Backgrounds", 0777);
                // the mkdir doesn't always properly set the permissions to 0777 so we're gonna chmod it ourselves
                chmod($LAUNCH["paths"]["share"]."Images/Backgrounds", 0777);
            }
            
                            
            // This will allow us to do directory operations
            $this->load->helper('directory');
            
            $objReturnData->objDirMap = directory_map($LAUNCH["paths"]["filestore"]);
            
            return $objReturnData;
            
        }
        
        
        
        // This will get us a custom directory listing based on the launch root.
        function getCustomListing($arrParams) {
        
            if ( !$this->authUser($arrParams[0], $arrParams[1], true) ) return $this->arrBadAuth;
            
            global $LAUNCH;
            
            // This will allow us to do directory operations
            $this->load->helper('directory');
            
            if ( is_dir($LAUNCH["paths"]["launch"].$arrParams[2]) ) return directory_map($LAUNCH["paths"]["launch"].$arrParams[2], true);
            else return array();
        
        }
        
        
        
        // This will grab the theme listing for us so we can use it in the 
        function getThemeListing($arrParams) {
            
            if ( !$this->authUser($arrParams[0], $arrParams[1], true) ) return $this->arrBadAuth;
            
            global $LAUNCH;
            
            $this->load->helper('directory');
            
            $arrThemeDirMap = directory_map($LAUNCH["paths"]["themes"], true);
            
            // This will hold the final theme listing.
            $arrThemeList = array();
            
            // Looping through each plugin and making sure all the files are in place and getting its info.xml file
            for ( $i = 0, $max = count($arrThemeDirMap); $i < $max; $i++ ) {
                // If the dir mapped item is a folder, we treat it as a theme, otherwise we ignore it.
                if ( is_dir($LAUNCH["paths"]["themes"].$arrThemeDirMap[$i]) ) array_push($arrThemeList, $arrThemeDirMap[$i]);
            }
            
            return $arrThemeList;
            
        }
        
        
        
        // This function will create a directory
        function createDir($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                global $LAUNCH;
                
                if ( !is_dir($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3]) ) {
                    mkdir($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3], 0777);
                    chmod($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3], 0777);
                    return true;
                }
                else return false;
            
            } else return $this->arrBadAuth;
        }
        
        
        
        // This function will move a file/directory to the trash
        function moveToTrash($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                global $LAUNCH;
                
                // The Trash Directory is manditory and will always be assured to be created
                if ( !is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/Trash") ) {
                    mkdir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/Trash", 0777);
                    chmod($LAUNCH["paths"]["userfiles"].$arrParams[0]."/Trash", 0777);
                }
                
                // Making sure this file/folder doesn't already exist in the Trash
                if ( !is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash/".$arrParams[3]) && !is_file($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash/".$arrParams[3]) ) {
                    
                    // Making sure the user isn't trying to delete the Desktop or the Trash
                    if ( ($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3] != $LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash") && ($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3] != $LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Desktop") ) {

                        // "renaming" our item into the trash
                        rename($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3], $LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash/".$arrParams[3]);
                        // returning success or failure
                        if ( is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash/".$arrParams[3]) || is_file($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash/".$arrParams[3]) ) return true;
                        else return false;
                        
                    } else return false;
                    
                } else return false;
                
            } else return $this->arrBadAuth;
        }
        
        
        
        // This function will move a file/directory to a specific location
        function moveFileOrFolder($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
                
                global $LAUNCH;
            
                // The location we're moving from, + the item name that's getting moved
                $strMoveFrom = $arrParams[2];
                $arrMoveFromArray = explode("/", $strMoveFrom);
                // The name of the item we're moving
                $strItemToMove = $arrMoveFromArray[count($arrMoveFromArray) - 1];
                
                // The location we're moving the item to
                $strMoveTo = $arrParams[3];
                
                if ( !is_dir($LAUNCH["paths"]["filestore"].$strMoveTo."/".$strItemToMove) && !is_file($LAUNCH["paths"]["filestore"].$strMoveTo."/".$strItemToMove) ) {
                    
                    // "renaming" our item to the new location
                    rename($LAUNCH["paths"]["filestore"].$strMoveFrom, $LAUNCH["paths"]["filestore"].$strMoveTo."/".$strItemToMove);
                    // returning success or failure
                    if ( is_dir($LAUNCH["paths"]["filestore"].$strMoveTo."/".$strItemToMove) || is_file($LAUNCH["paths"]["filestore"].$strMoveTo."/".$strItemToMove) ) return true;
                    else return false;
                    
                } else return false;
                
            
            } else return $this->arrBadAuth;
        }
        
        
        
        // This function will delete a passed in file or folder
        function deleteFileOrFolder($arrParams) {
        
            if ( !$this->authUser($arrParams[0], $arrParams[1], true) ) return $this->arrBadAuth;
            
            global $LAUNCH;
            
            // Checking if this is a file
            if ( is_file($LAUNCH["paths"]["filestore"].$arrParams[2]) ) {
                
                // returning true of the file is deleted successfully
                if ( unlink($LAUNCH["paths"]["filestore"].$arrParams[2]) ) return true;
                else return false;
            
            }
            // Checking if this is a folder
            if ( is_dir($LAUNCH["paths"]["filestore"].$arrParams[2]) ) {
                
                // returning true if the folder is deleted successfully
                if ( rmdir($LAUNCH["paths"]["filestore"].$arrParams[2]) ) return true;
                else return false;
            
            }
            // If it's not a file or folder, we return false.
            else return false;
        
        }
        
        
        
        // This function will rename a file/directory
        function renameFileOrFolder($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
                
                global $LAUNCH;
                
                $strTarget = $arrParams[2];
                $arrTargetArray = explode("/", $strTarget);
                $strOldFileName = array_pop($arrTargetArray);   // Saving the old "target" and removing it from the target array
                $strNewFileName = $arrParams[3];
                $strTarget = implode("/", $arrTargetArray);     // Combining the target array into one string
                
                // making sure it doesn't already exist
                if ( !is_dir($LAUNCH["paths"]["filestore"].$strTarget."/".$strNewFileName) && !is_file($LAUNCH["paths"]["filestore"].$strTarget."/".$strNewFileName) ) {
                    
                    //renaming our item
                    rename($LAUNCH["paths"]["filestore"].$strTarget."/".$strOldFileName, $LAUNCH["paths"]["filestore"].$strTarget."/".$strNewFileName);
                    
                    // Making sure the item renamed properly
                    if ( is_dir($LAUNCH["paths"]["filestore"].$strTarget."/".$strNewFileName) || is_file($LAUNCH["paths"]["filestore"].$strTarget."/".$strNewFileName) ) return true;
                    else return false;
                    
                } else return false;
                
            } else return $this->arrBadAuth;
        }
        
        
        
        // this function will empty the current users trash
        function emptyTrash($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                global $LAUNCH;
                
                // Emptying the trash directory of this user
                if ( $this->emptyDirectory($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash", true) ) return true;
                else return false;
                
            } else return $this->arrBadAuth;
        }
        
        

        // --------  Recursive Directory Delete PHP function ---------
        // Got this from http://www.dreamincode.net/code/snippet1225.htm
        function emptyDirectory($directory, $empty=FALSE) {
        
             // if the path has a slash at the end we remove it here
             if(substr($directory,-1) == '/') {
                  $directory = substr($directory,0,-1);
             }
             // if the path is not valid or is not a directory ...
             if(!file_exists($directory) || !is_dir($directory)) {
                  // ... we return false and exit the function
                  return FALSE;
             }
             // ... if the path is not readable
             elseif (!is_readable($directory)) {
                  // ... we return false and exit the function
                  return FALSE;
             }
             // ... else if the path is readable
             else {
                  // we open the directory
                  $handle = opendir($directory);
                  // and scan through the items inside
                  while (FALSE !== ($item = readdir($handle))) {
                       // if the filepointer is not the current directory
                       // or the parent directory
                       if($item != '.' && $item != '..') {
                            // we build the new path to delete
                            $path = $directory.'/'.$item;
                            // if the new path is a directory
                            if(is_dir($path)) {
                                 // we call this function with the new path
                                 $this->emptyDirectory($path);
                            // if the new path is a file
                            }
                            else {
                                 // we remove the file
                                 unlink($path);
                            }
                       }
                  }
                  // close the directory
                  closedir($handle);
                  // if the option to empty is not set to true
                  if($empty == FALSE) {
                       // try to delete the now empty directory
                       if(!rmdir($directory)) {
                            // return false if not possible
                            return FALSE;
                       }
                  }
                  // return success
                  return TRUE;
             }
        }
        // ------------------------End Of Function----------------------------
        
        
        
        
        /*-----------------------------------------------//
        //-- THESE FUNCTIONS ARE FOR PLUGIN OPERATIONS --//
        //-----------------------------------------------*/
        
        // This function will return a directory listing of the plugins directory as well as set up anything that needs to be set up for the plugins table
        function getPluginListing($arrParams) {
            if ( !$this->authUser($arrParams[0], $arrParams[1], true) ) return $this->arrBadAuth;
            
            global $LAUNCH;
            
            // This will allow us to do directory operations
            $this->load->helper('directory');
            $this->load->helper('launch_xml_reader');
                        
            
            
            /* -- PLUGIN DIRECTORY HANDLING -- */
            // Getting the directory listing of the plugins directory
            $arrDirPlugins = directory_map($LAUNCH["paths"]["plugins"], true);
            
            // Looping through each plugin and making sure all the files are in place and getting its info.xml file
            for ( $i = 0, $max = count($arrDirPlugins); $i < $max; $i++ ) {
                
                // Making sure each item in the plugins directory is a directory and has the needed files in it.
                if (    is_dir($LAUNCH["paths"]["plugins"].$arrDirPlugins[$i]) &&
                        is_file($LAUNCH["paths"]["plugins"].$arrDirPlugins[$i]."/info.xml") &&
                        is_file($LAUNCH["paths"]["plugins"].$arrDirPlugins[$i]."/index.php") )  {
                    
                    
                    // Holding on to the directory name so we can use it later.
                    $strPluginDir = $arrDirPlugins[$i];
                    
                    // Getting the plugin's information from its xml file.
                    $arrPluginData = xml2array( file_get_contents($LAUNCH["paths"]["plugins"].$arrDirPlugins[$i]."/info.xml") );
                    $key = array_keys($arrPluginData);
                    $arrDirPlugins[$i] = $arrPluginData[$key[0]];
                    
                    // Saving the original directory name as part of the directory attributes
                    $arrDirPlugins[$i]["dir"] = $strPluginDir;
                
                }
                else unset($arrDirPlugins[$i]);
                
            }
            // Reindexing the array of directory plugins
            $arrDirPlugins = array_values($arrDirPlugins);
            
            
            
            /* -- PLUGINS DB TABLE HANDLING -- */
            // Getting all the plugins out of the database that are currently in there.
            $this->db->from("plugins");
            $arrDBPlugins = $this->select();
            
            // Removing any plugins from the database that are no longer in the plugins directory
            for ( $i = 0, $max = count($arrDBPlugins); $i < $max; $i++ ) {
            
                $boolInPluginList = false;
                
                foreach ( $arrDirPlugins as $arrDirPlugin ) {
                    if ( $arrDirPlugin["name"] == $arrDBPlugins[$i]->name ) $boolInPluginList = true;
                }
                
                // If the plugin from the database isn't in the list of plugins, we want to remove it from the database
                if ( !$boolInPluginList ) {
                    $this->db->where("plugin_id", $arrDBPlugins[$i]->plugin_id);
                    $this->db->delete("plugins");
                    unset($arrDBPlugins[$i]);
                }
            
            }
            //Reindexing the array of db plugins
            $arrDBPlugins = array_values($arrDBPlugins);
            
            
            
            /* -- PLUGINS DIR AND DB SYNCING -- */
            // Looping through every plugin directory and making sure it's been added to the database.
            for ( $i = 0, $max = count($arrDirPlugins); $i < $max; $i++ ) {
                
                $boolPluginInDB = false;
                
                // Adding the "enabled" value to the plugin and setting it to the default value
                // If the plugin is already in the database, this value will be updated based on the stored value
                $arrDirPlugins[$i]["enabled"] = "0";
                
                // Looping through each db plugin and seeing if a plugin in the dir is also installed in the database
                // If it's in the DB, we want to get whatever its enabled status is.
                foreach ( $arrDBPlugins as $objDBPlugin ) {
                    if ( $objDBPlugin->name == $arrDirPlugins[$i]["name"] ) {
                        $boolPluginInDB = true;
                        $arrDirPlugins[$i]["enabled"] = $objDBPlugin->enabled;
                    }
                }
                
                // If the directory plugin isn't in the DB, we want to insert it into the plugins table
                if ( !$boolPluginInDB ) {
                
                    $arrData = array(
                        "display_name"  =>  $arrDirPlugins[$i]["display_name"],
                        "dir"           =>  $arrDirPlugins[$i]["dir"],
                        "name"          =>  $arrDirPlugins[$i]["name"],
                        "description"   =>  $arrDirPlugins[$i]["description"],
                        "version"       =>  $arrDirPlugins[$i]["version"],
                        "url"           =>  $arrDirPlugins[$i]["url"]
                    );
                    $this->db->insert("plugins", $arrData);
                    
                }
            
            }
            
            
            return $arrDirPlugins;
            
        }
        
        
        // This function will change a plugin's status
        function changePluginStatus($arrParams) {
            if ( !$this->authUser(array_shift($arrParams), array_shift($arrParams), true) ) return $this->arrBadAuth;
            
            global $LAUNCH;
            
            $intEnable = $arrParams[0];
            $strPlugin = $arrParams[1];
            
            // Getting the plugin in question out of the database.
            $this->db->from("plugins");
            $this->db->where("name", $strPlugin);
            $arrPlugin = $this->select();
            
            // Making sure we got one row from the database
            if ( count($arrPlugin) != 1 ) return false;
            else $objPlugin = $arrPlugin[0];
            
            
            // Setting the enabled value in the database to what we have passed in.
            $this->db->set("enabled", $intEnable);
            $this->db->where("name", $strPlugin);
            $this->db->update("plugins");
            
            
            // If we're enabling a plugin, we want to go through its installer process
            if ( $intEnable == "1" && file_exists($LAUNCH["paths"]["plugins"].$objPlugin->dir."/install.php") ) {
                
                require($LAUNCH["paths"]["plugins"].$objPlugin->dir."/install.php");
                
                if ( class_exists("install_".$strPlugin."_plugin") ) {
                    $install_plugin_class = "install_".$strPlugin."_plugin";
                    $objInstallPlugin = new $install_plugin_class();
                    
                    if ( method_exists($objInstallPlugin, "install") ) {
                        $strReturnString = $objInstallPlugin->install();
                        
                        // If the installer passed back a string, we return the string for the user's benefit
                        if ( is_string($strReturnString) ) return $strReturnString;
                    }
                
                }
            
            }
            elseif ( $intEnable == "0" ) return $objPlugin->display_name." Plugin Disabled.";
            
            return true;
            
        }
        

        
    }   // End of File

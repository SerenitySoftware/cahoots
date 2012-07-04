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
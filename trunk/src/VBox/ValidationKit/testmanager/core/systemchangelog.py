# -*- coding: utf-8 -*-
# $Id$

"""
Test Manager - System changelog compilation.
"""

__copyright__ = \
"""
Copyright (C) 2012-2016 Oracle Corporation

This file is part of VirtualBox Open Source Edition (OSE), as
available from http://www.virtualbox.org. This file is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License (GPL) as published by the Free Software
Foundation, in version 2 as it comes in the "COPYING" file of the
VirtualBox OSE distribution. VirtualBox OSE is distributed in the
hope that it will be useful, but WITHOUT ANY WARRANTY of any kind.

The contents of this file may alternatively be used under the terms
of the Common Development and Distribution License Version 1.0
(CDDL) only, as it comes in the "COPYING.CDDL" file of the
VirtualBox OSE distribution, in which case the provisions of the
CDDL are applicable instead of those of the GPL.

You may elect to license modified versions of this file under the
terms and conditions of either the GPL or the CDDL or both.
"""
__version__ = "$Revision$"


# Validation Kit imports.
from testmanager.core.base import ModelLogicBase;
from testmanager.core.useraccount import UserAccountLogic;


class SystemChangelogEntry(object): # pylint: disable=R0902
    """
    System changelog entry.
    """

    def __init__(self, tsEffective, oAuthor, sWhat, idWhat, sDesc):
        self.tsEffective = tsEffective;
        self.oAuthor     = oAuthor;
        self.sWhat       = sWhat;
        self.idWhat      = idWhat;
        self.sDesc       = sDesc;


class SystemChangelogLogic(ModelLogicBase):
    """
    System changelog compilation logic.
    """

    ## @name What kind of change.
    ## @{
    ksWhat_TestBox          = 'TestBox';
    ksWhat_TestCase         = 'TestCase';
    ksWhat_Blacklisting     = 'Blacklisting';
    ksWhat_Build            = 'Build';
    ksWhat_BuildSource      = 'BuildSource';
    ksWhat_FailureCategory  = 'FailureCategory';
    ksWhat_FailureReason    = 'FailureReason';
    ksWhat_GlobalRsrc       = 'GlobalRsrc';
    ksWhat_SchedGroup       = 'SchedGroup';
    ksWhat_SystemLog        = 'SystemLog';
    ksWhat_TestGroup        = 'TestGroup';
    ksWhat_User             = 'User';
    ksWhat_TestResult       = 'TestResult';
    ## @}

    ## The table key is the effective timestamp.
    ksClue_TimestampId = 'TimestampId';

    ## Mapping a changelog entry kind to a table, key and clue.
    kdWhatToTable = {
        ksWhat_TestBox:          ( 'TestBoxes',          'idTestBox',           None, ),
        ksWhat_TestCase:         ( 'TestCasees',         'idTestCase',          None, ),
        ksWhat_Blacklisting:     ( 'Blacklist',          'idBlacklisting',      None, ),
        ksWhat_Build:            ( 'Builds',             'idBuild',             None, ),
        ksWhat_BuildSource:      ( 'BuildSources',       'idBuildSrc',          None, ),
        ksWhat_FailureCategory:  ( 'FailureCategories',  'idFailureCategory',   None, ),
        ksWhat_FailureReason:    ( 'FailureReasons',     'idFailureReason',     None, ),
        ksWhat_GlobalRsrc:       ( 'GlobalResources',    'idGlobalRsrc',        None, ),
        ksWhat_SchedGroup:       ( 'SchedGroupes',       'idSchedGroup',        None, ),
        ksWhat_SystemLog:        ( 'SystemLog',          'tsCreated',           ksClue_TimestampId, ),
        ksWhat_TestGroup:        ( 'TestGroupes',        'idTestGroup',         None, ),
        ksWhat_User:             ( 'Users',              'idUser',              None, ),
        ksWhat_TestResult:       ( 'TestResults',        'idTestResult',        None, ),
    };

    ## @todo move to config.py?
    ksVSheriffLoginName = 'vsheriff';


    ## @name for kaasChangelogTables
    ## @internal
    ## @{
    ksTweak_None                    = '';
    ksTweak_NotNullAuthor           = 'uidAuthorNotNull';
    ksTweak_NotNullAuthorOrVSheriff = 'uidAuthorNotNullOrVSheriff';
    ## @}

    ## @internal
    kaasChangelogTables = (
        # [0]: change name,       [1]: Table name,          [2]: key column,     [3]:later,    [4]: tweak
        ( ksWhat_TestBox,         'TestBoxes',              'idTestBox',         None,         ksTweak_NotNullAuthor, ),
        ( ksWhat_TestBox,         'TestBoxesInSchedGroups', 'idTestBox',         None,         ksTweak_None, ),
        ( ksWhat_TestCase,        'TestCases',              'idTestCase',        None,         ksTweak_None, ),
        ( ksWhat_TestCase,        'TestCaseArgs',           'idTestCase',        None,         ksTweak_None, ),
        ( ksWhat_TestCase,        'TestCaseDeps',           'idTestCase',        None,         ksTweak_None, ),
        ( ksWhat_TestCase,        'TestCaseGlobalRsrcDeps', 'idTestCase',        None,         ksTweak_None, ),
        ( ksWhat_Blacklisting,    'BuildBlacklist',         'idBlacklisting',    None,         ksTweak_None, ),
        ( ksWhat_Build,           'Builds',                 'idBuild',           None,         ksTweak_NotNullAuthor, ),
        ( ksWhat_BuildSource,     'BuildSources',           'idBuildSrc',        None,         ksTweak_None, ),
        ( ksWhat_FailureCategory, 'FailureCategories',      'idFailureCategory', None,         ksTweak_None, ),
        ( ksWhat_FailureReason,   'FailureReasons',         'idFailureReason',   None,         ksTweak_None, ),
        ( ksWhat_GlobalRsrc,      'GlobalResources',        'idGlobalRsrc',      None,         ksTweak_None, ),
        ( ksWhat_SchedGroup,      'SchedGroups',            'idSchedGroup',      None,         ksTweak_None, ),
        ( ksWhat_SchedGroup,      'SchedGroupMembers',      'idSchedGroup',      None,         ksTweak_None, ),
        ( ksWhat_TestGroup,       'TestGroups',             'idTestGroup',       None,         ksTweak_None, ),
        ( ksWhat_TestGroup,       'TestGroupMembers',       'idTestGroup',       None,         ksTweak_None, ),
        ( ksWhat_User,            'Users',                  'uid',               None,         ksTweak_None, ),
        ( ksWhat_TestResult,      'TestResultFailures',     'idTestResult',      None,         ksTweak_NotNullAuthorOrVSheriff, ),
    );

    def __init__(self, oDb):
        ModelLogicBase.__init__(self, oDb);


    def fetchForListingEx(self, iStart, cMaxRows, tsNow, cDaysBack):
        """
        Fetches SystemLog entries.

        Returns an array (list) of SystemLogData items, empty list if none.
        Raises exception on error.
        """

        #
        # Construct the query.
        #
        oUserAccountLogic = UserAccountLogic(self._oDb);
        oVSheriff   = oUserAccountLogic.tryFetchAccountByLoginName(self.ksVSheriffLoginName);
        uidVSheriff = oVSheriff.uid if oVSheriff is not None else -1;

        if tsNow is None:
            sWhereTime = self._oDb.formatBindArgs('    WHERE  tsEffective >= CURRENT_TIMESTAMP - \'%s days\'::interval\n',
                                                  (cDaysBack,));
        else:
            sWhereTime = self._oDb.formatBindArgs('    WHERE  tsEffective >= (%s::timestamptz - \'%s days\'::interval)\n'
                                                  '       AND tsEffective <= %s\n',
                                                  (tsNow, cDaysBack, tsNow));

        # Special entry for the system log.
        sQuery  = '(\n'
        sQuery += '    SELECT NULL AS uidAuthor,\n';
        sQuery += '           tsCreated as tsEffective,\n';
        sQuery += '           \'' + self.ksWhat_SystemLog + '\' AS sWhat,\n';
        sQuery += '           NULL AS idWhat,\n';
        sQuery += '           CONCAT(sEvent, \': \', sLogText) AS sDesc\n';
        sQuery += '    FROM   SystemLog\n';
        sQuery += sWhereTime.replace('tsEffective', 'tsCreated');
        sQuery += '    ORDER BY tsCreated DESC\n'
        sQuery += ')'

        for asEntry in self.kaasChangelogTables:
            sQuery += ' UNION (\n'
            sQuery += '    SELECT uidAuthor, tsEffective, \'' + asEntry[0] + '\', ' + asEntry[2] + ', \'\'\n';
            sQuery += '    FROM   ' + asEntry[1] + '\n'
            sQuery += sWhereTime;
            if asEntry[4] == self.ksTweak_NotNullAuthor or asEntry[4] == self.ksTweak_NotNullAuthorOrVSheriff:
                sQuery += '      AND uidAuthor IS NOT NULL\n';
                if asEntry[4] == self.ksTweak_NotNullAuthorOrVSheriff:
                    sQuery += '      AND uidAuthor <> %u\n' % (uidVSheriff,);
            sQuery += '    ORDER BY tsEffective DESC\n'
            sQuery += ')';
        sQuery += ' ORDER BY 2 DESC\n';
        sQuery += '  LIMIT %u OFFSET %u\n' % (cMaxRows, iStart, );


        #
        # Execute the query and construct the return data.
        #
        self._oDb.execute(sQuery);
        aoRows = [];
        for aoRow in self._oDb.fetchAll():
            aoRows.append(SystemChangelogEntry(aoRow[1], oUserAccountLogic.cachedLookup(aoRow[0]),
                                               aoRow[2], aoRow[3], aoRow[4]));


        return aoRows;


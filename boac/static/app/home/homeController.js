/**
 * Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

(function(angular) {

  'use strict';

  angular.module('boac').controller('HomeController', function(
    cohortFactory,
    config,
    studentGroupFactory,
    $rootScope,
    $scope
  ) {

    var extendSortableNames = function(students) {
      return _.map(students, function(student) {
        return _.extend(student, {
          sortableName: student.lastName + ', ' + student.firstName
        });
      });
    };

    var loadMyCohorts = function(callback) {
      cohortFactory.getMyCohorts().then(function(cohortsResponse) {
        $rootScope.myCohorts = [];

        _.each(cohortsResponse.data, function(cohort) {
          if (cohort.alerts.length) {
            cohort.alerts = {
              isCohortAlerts: true,
              students: extendSortableNames(cohort.alerts),
              sortBy: 'sortableName',
              reverse: false
            };
          }
          $rootScope.myCohorts.push(cohort);
        });
        return callback();
      });
    };

    var loadMyStudentGroups = function(callback) {
      studentGroupFactory.getMyStudentGroups().then(function(response) {
        var groups = response.data;
        $rootScope.myGroups = [];
        _.each(groups, function(group) {
          var decoratedGroup = {
            id: group.id,
            name: group.name,
            students: extendSortableNames(group.students),
            sortBy: 'sortableName',
            reverse: false
          };
          if (group.name === 'My Students') {
            $rootScope.myPrimaryGroup = decoratedGroup;
          } else {
            $rootScope.myGroups.push(group);
          }
        });
        return callback();
      });
    };

    var init = function() {
      $scope.isLoading = true;

      loadMyStudentGroups(function() {
        loadMyCohorts(function() {
          $scope.isLoading = false;
        });
      });
    };

    $rootScope.$on('myCohortsUpdated', function() {
      $scope.isLoading = true;
      loadMyCohorts(function() {
        $scope.isLoading = false;
      });
    });

    init();
  });

}(window.angular));

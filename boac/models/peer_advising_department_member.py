"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""


from boac import db
from boac.models.base import Base
from sqlalchemy.dialects.postgresql import ENUM

role_types = ENUM(
    'peer_advisor',
    'peer_advisor_manager',
    name='role_types',
    create_type=False,
)


class PeerAdvisingDepartmentMember(Base):
    __tablename__ = 'peer_advising_department_members'

    role_type = db.Column(role_types, nullable=False)
    peer_advising_department_id = db.Column(db.Integer, db.ForeignKey('peer_advising_departments.id'), nullable=False, primary_key=True)
    authorized_user_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False, primary_key=True)
    deleted_at = db.Column(db.DateTime)

    peer_advising_department = db.relationship('PeerAdvisingDepartment', back_populates='peer_advising_department_members')
    authorized_user = db.relationship('AuthorizedUser', back_populates='peer_advising_department_memberships')

    def __init__(self, name, peer_advising_department_id, authorized_user_id, role_type, deleted_at):
        self.name = name
        self.role_type = role_type
        self.peer_advising_department_id = peer_advising_department_id
        self.authorized_user_id = authorized_user_id
        self.deleted_at = deleted_at

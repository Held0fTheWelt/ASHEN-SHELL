from app.extensions import db


class User(db.Model):
    """User for auth (web session and API JWT). Primary role via Role model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    email_verified_at = db.Column(db.DateTime(timezone=True), nullable=True, default=None)

    role_rel = db.relationship("Role", backref="users", lazy="joined")

    ROLE_USER = "user"
    ROLE_MODERATOR = "moderator"
    ROLE_EDITOR = "editor"
    ROLE_ADMIN = "admin"

    @property
    def role(self) -> str:
        """Role name for API/templates. Use has_role / is_admin for checks."""
        return self.role_rel.name if self.role_rel else self.ROLE_USER

    def has_role(self, name: str) -> bool:
        """True if this user has the given role name."""
        return (self.role_rel and self.role_rel.name == name) or self.role == name

    def has_any_role(self, names) -> bool:
        """True if this user has any of the given role names."""
        r = self.role_rel.name if self.role_rel else self.role
        return r in names

    @property
    def is_admin(self) -> bool:
        """True if this user has admin role."""
        return self.has_role(self.ROLE_ADMIN)

    @property
    def is_moderator_or_admin(self) -> bool:
        """True if this user has moderator or admin role."""
        return self.has_any_role((self.ROLE_MODERATOR, self.ROLE_ADMIN))

    def to_dict(self, include_email: bool = False):
        out = {"id": self.id, "username": self.username, "role": self.role}
        if include_email:
            out["email"] = self.email
        return out

    def can_write_news(self):
        """True if this user may create/update/delete/publish news."""
        return self.role in (self.ROLE_EDITOR, self.ROLE_ADMIN)

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"

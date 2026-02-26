from __future__ import annotations

from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(required=True)
    username = fields.Str(required=True)
    created_at = fields.DateTime(required=True)


class CreateUserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, mobile, password, **extra_fields):
        """
        Create and save a user with the given mobile or phone and password.
        """
        if not mobile:
            raise ValueError("The mobile must be set.")
        if email := extra_fields.get("email"):
            email = self.normalize_email(email)
            extra_fields["email"] = email
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mobile=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(mobile, password, **extra_fields)

    def create_superuser(self, mobile=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(mobile, password, **extra_fields)

from django.contrib.auth.models import UserManager
import logging
logger = logging.getLogger(__name__)

class CustomUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, mobile, password, **extra_fields):
        logger.info("Entering _create_user")
        """
        Create and save a user with the given mobile or phone and password.
        """
        if not mobile:
            logger.error("The mobile must be set.")
            raise ValueError("The mobile must be set.")
        if email := extra_fields.get("email"):
            email = self.normalize_email(email)
            extra_fields["email"] = email
            logger.info(f"Email normalized: {email}")
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        logger.info("Exiting _create_user")
        return user

    def create_user(self, mobile=None, password=None, **extra_fields):
        logger.info("Entering create_user")
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        logger.info("Exiting create_user")
        return self._create_user(mobile, password, **extra_fields)

    def create_superuser(self, mobile=None, password=None, **extra_fields):
        logger.info("Entering create_superuser")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            logger.error("Superuser must have is_staff=True.")
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            logger.error("Superuser must have is_superuser=True.")
            raise ValueError("Superuser must have is_superuser=True.")
        logger.info("Exiting create_superuser")
        return self._create_user(mobile, password, **extra_fields)

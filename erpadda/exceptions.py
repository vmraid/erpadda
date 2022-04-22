import vmraid


# accounts
class PartyFrozen(vmraid.ValidationError):
	pass


class InvalidAccountCurrency(vmraid.ValidationError):
	pass


class InvalidCurrency(vmraid.ValidationError):
	pass


class PartyDisabled(vmraid.ValidationError):
	pass


class InvalidAccountDimensionError(vmraid.ValidationError):
	pass


class MandatoryAccountDimensionError(vmraid.ValidationError):
	pass

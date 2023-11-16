export enum AUTH_PROVIDERS {
	LOCAL = 'local',
	FB = 'facebook',
}

export interface IUserRole {
	code: string;
	_id: string;
}

export interface IUserInfo {
	email?: string;
	_id: string;
}

export interface IUserConfirmation {
	code: string | null;
	ts: Date | null;
}
export interface IUserResetPassword {
	code: string | null;
	tmpPassword: string | null;
	ts: Date | null;
}
export interface IUserAgreements {
	terms: boolean;
	privacy: boolean;
	commercial: boolean;
	ts: Date;
}

interface IUser {
	email: string;
	lang: string;
	firstName: string;
	lastName: string;
	confirmed: boolean;
	blocked: boolean;
	providers: [AUTH_PROVIDERS];
	password: string;
	role: IUserRole;
	agreements: IUserAgreements;
	createdBy: IUserInfo;
	updatedBy: IUserInfo;
	// tslint:disable-next-line:ban-types
	isAdmin: Function;
	// tslint:disable-next-line:ban-types
	isEditor: Function;
	confirmation?: IUserConfirmation;
	resetPassword?: IUserResetPassword;
	passwordHistory: { ts: Date; password: string }[];
}

export { IUser };

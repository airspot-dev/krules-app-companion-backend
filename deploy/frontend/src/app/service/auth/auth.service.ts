import { Injectable } from '@angular/core';
import {
  Auth,
  signInWithEmailAndPassword,
  authState,
  User,
  user as user$,
} from '@angular/fire/auth';
import { from, map, Observable } from 'rxjs';
import { GlobalsService } from '../globals/globals.service';
import { KrulesService } from '../krules/krules.service';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  // currentUser$ = authState(this.auth);
  user?: User;
  fbAuth: Auth;
  _currentProject: string = '';
  constructor(private auth: Auth, private _krules: KrulesService) {
    this.fbAuth = auth;
  }

  getFireToken() {
    return user$(this.fbAuth).pipe(
      map((user: any) => {
        return (user as any).accessToken;
      })
    );
  }

  setCurrentProject(project: string) {
    this._currentProject = project;
    localStorage.setItem('current_project', project);
    window.location.reload();
  }

  getCurrentProject() {
    return this._currentProject;
  }

  init() {
    const lsUser = localStorage.getItem('user');
    this._currentProject = localStorage.getItem('current_project') || '';
    if (lsUser) {
      this.user = JSON.parse(lsUser);
    }
  }

  login(email: string, password: string): Observable<any> {
    return from(
      signInWithEmailAndPassword(this.auth, email, password)
        .then((data) => {
          this.user = data.user;
          localStorage.setItem('user', JSON.stringify({ ...data.user }));
          return this._krules.getAvailableProjects(
            (this.user as any).accessToken
          );
        })
        .then((result: any) => {
          this.setCurrentProject(result.active_subscription);
        })
    );
  }

  logout(): Observable<any> {
    return from(
      this.auth.signOut().then(() => {
        localStorage.removeItem('user');
      })
    );
  }
}

import {
  concatAll,
  filter,
  from,
  last,
  map,
  Observable,
  of,
  pipe,
  switchMap,
} from 'rxjs';
import { Configuration } from 'src/app/app.constants';
import { IService } from './interface/iservice';
import {
  addDoc,
  collection,
  Firestore,
  collectionData,
  deleteDoc,
  onSnapshot,
  doc,
  DocumentData,
  getDoc,
  DocumentSnapshot,
  and,
  DocumentReference,
  WithFieldValue,
  setDoc,
  orderBy,
  query,
  limit,
  getDocs,
  Query,
  getCountFromServer,
  startAfter,
  endBefore,
  getDocsFromServer,
  updateDoc,
  documentId,
  increment,
} from '@angular/fire/firestore';
import { Auth, user as user$ } from '@angular/fire/auth';

import { AuthService } from '../auth/auth.service';
import { User } from '@angular/fire/auth';
import { limitToLast, OrderByDirection } from 'firebase/firestore';

export interface IQueryOptions {
  query?: any[];
  path?: string;
  startAfter?: string;
  endBefore?: string;
  order?: { [key: string]: string };
  pageNumber?: number;
  pageSize?: number;
}
export interface IUpdateOptions {
  query?: any[];
  path?: string;
  merge?: boolean;
}
export class ServiceBase<T> /* implements IService<T> */ {
  collectionName: string;
  user?: User;
  constructor(
    collectionName: string,
    _configuration: Configuration,
    private fs: Firestore,
    protected _auth: AuthService
  ) {
    this.collectionName = collectionName;
    this.user = this._auth.user;
  }

  protected _getSubscriptionId() {
    return this._auth.getCurrentProject();
    // let customAttributes;
    // try {
    //   customAttributes = (this.user as any).reloadUserInfo.customAttributes;
    //   customAttributes = JSON.parse(customAttributes);
    // } catch (error) {
    //   console.error(error);
    // }
    // return customAttributes.subscription_id;
  }

  protected _getCollectionPath() {
    return `/${this._getSubscriptionId()}/${this.collectionName}`;
  }

  getMaxValue(key: string) {
    return getDocs(
      query(
        collection(this.fs, this._getCollectionPath()),
        orderBy(key, 'desc'),
        limit(1)
      )
    );
  }

  getById(id: string): Promise<DocumentSnapshot<DocumentData>> {
    let collectionName = this._getCollectionPath();
    let docRef = doc(this.fs, `${collectionName}/${id}`);
    return getDoc(docRef);
  }

  count(options: IQueryOptions) {
    let collectionName = this._getCollectionPath();
    if (options.path) collectionName = collectionName + options.path;

    let coll = collection(this.fs, collectionName);
    const queries: any[] = [];
    if (options.query && options.query.length)
      options.query.forEach((q) => queries.push(q));
    const q = query(coll, ...queries);
    return getCountFromServer(q);
  }

  getAllReactive(options: IQueryOptions = {}) {
    let queries: any[] = [];
    if (options.order) {
      Object.keys(options.order).forEach((key) => {
        queries.push(orderBy(key, options.order![key] as OrderByDirection));
      });
    }
    if (options.pageSize) {
      if (options.order && options.endBefore)
        queries.push(limitToLast(options.pageSize));
      else queries.push(limit(options.pageSize));
    }
    let collectionName = this._getCollectionPath();
    if (options.path) collectionName = collectionName + options.path;
    // next page
    if (options.order && options.startAfter)
      queries.push(startAfter(options.startAfter));
    // previus page
    if (options.order && options.endBefore)
      queries.push(endBefore(options.endBefore));
    // query
    if (options.query) queries = queries.concat(options.query);

    let coll = collection(this.fs, collectionName);
    const q = query(coll, ...queries);

    return collectionData(q, { idField: 'id' });
  }

  private _buildReadQuery(options: IQueryOptions = {}) {
    let queries: any[] = [];
    if (options.order) {
      Object.keys(options.order).forEach((key) => {
        queries.push(orderBy(key, options.order![key] as OrderByDirection));
      });
    }
    if (!options.order /* && (options.startAfter || options.endBefore) */) {
      queries.push(orderBy(documentId(), 'asc'));
    }
    if (options.pageSize) {
      if (options.order && options.endBefore)
        queries.push(limitToLast(options.pageSize));
      else queries.push(limit(options.pageSize));
    }
    let collectionName = this._getCollectionPath();
    if (options.path) collectionName = collectionName + options.path;
    // next page
    if (options.startAfter) queries.push(startAfter(options.startAfter));
    // previus page
    if (options.endBefore) queries.push(endBefore(options.endBefore));
    // query
    if (options.query) queries = queries.concat(and(...options.query));

    let coll = collection(this.fs, collectionName);

    return query(coll, ...queries);
  }

  getAllRealTime(options: IQueryOptions = {}, cb: any) {
    const q = this._buildReadQuery(options);
    return onSnapshot(q, cb);
  }

  getAll(options: IQueryOptions = {}) {
    const q = this._buildReadQuery(options);

    return getDocsFromServer(q);
  }

  create(model: T): Observable<DocumentReference<DocumentData>> {
    const coll = this._getCollectionPath();
    return from(
      addDoc(collection(this.fs, coll), model as WithFieldValue<DocumentData>)
    );
  }

  upsertById(id: string, model: T, options: IUpdateOptions = {}) {
    let coll = this._getCollectionPath();
    if (options.path) coll = coll + options.path;
    let docRef = doc(this.fs, coll, id);
    return updateDoc(docRef, model as WithFieldValue<DocumentData>);
  }

  incrementFiledById(id: string, field: string, inc: number) {
    let coll = this._getCollectionPath();
    let docRef = doc(this.fs, coll, id);
    const obj: any = {};
    obj[field] = increment(inc);
    return updateDoc(docRef, obj);
  }
  updateById(id: string, model: T, options: IUpdateOptions = {}) {
    let coll = this._getCollectionPath();
    if (options.path) coll = coll + options.path;
    let docRef = doc(this.fs, coll, id);
    const opts: any = {};
    if (options.merge) opts.merge = true;
    return setDoc(docRef, model as WithFieldValue<DocumentData>, opts);
  }

  deleteById(id: string) {
    const coll = this._getCollectionPath();
    let docRef = doc(this.fs, `${coll}/${id}`);
    return from(deleteDoc(docRef));
  }
}

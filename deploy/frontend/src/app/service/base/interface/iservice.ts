import { User } from '@angular/fire/auth';
import {
  CollectionReference,
  DocumentData,
  DocumentReference,
  DocumentSnapshot,
} from '@angular/fire/firestore';
import { Observable } from 'rxjs';

export interface IService<T> {
  collectionName: string;
  collectionPath?: string;
  user: User | null;
  getById(id: string): Promise<DocumentSnapshot<DocumentData>>;
  getMaxValue(key: string): Observable<T[]>;
  getAll(): Observable<T[]>;
  create(model: any): Promise<DocumentReference<DocumentData>>;
  updateById(id: string, model: T): Promise<void>;
  deleteById(id: string): Promise<void>;
}

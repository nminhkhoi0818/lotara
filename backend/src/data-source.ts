import { DataSource } from 'typeorm';
import { config } from 'dotenv';
import * as path from 'path';
import * as fs from 'fs';

config();

// Determine if we're running from src (dev) or dist (prod)
const isProduction = __dirname.includes('dist');
const rootDir = isProduction ? 'dist' : 'src';

export const AppDataSource = new DataSource({
  type: 'postgres',
  host: process.env.POSTGRES_HOST ?? 'localhost',
  port: Number(process.env.POSTGRES_PORT ?? 5432),
  username: process.env.POSTGRES_USER ?? 'lotara',
  password: process.env.POSTGRES_PASSWORD ?? 'lotara',
  database: process.env.POSTGRES_DB ?? 'lotara',
  entities: [`${rootDir}/**/*.entity.{ts,js}`],
  migrations: [`${rootDir}/migrations/*.{ts,js}`],
  synchronize: false,
});

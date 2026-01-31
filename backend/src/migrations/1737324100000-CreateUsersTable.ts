import { MigrationInterface, QueryRunner, Table } from 'typeorm';

export class CreateUsersTable1737324100000 implements MigrationInterface {
  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.createTable(
      new Table({
        name: 'users',
        columns: [
          {
            name: 'id',
            type: 'uuid',
            isPrimary: true,
            generationStrategy: 'uuid',
            default: 'uuid_generate_v4()',
          },
          {
            name: 'vibe_vector',
            type: 'jsonb',
            isNullable: false,
          },
          {
            name: 'budget_range',
            type: 'varchar',
            length: '50',
            isNullable: false,
          },
          {
            name: 'travel_style',
            type: 'varchar',
            length: '50',
            isNullable: false,
          },
          {
            name: 'persona_answers',
            type: 'jsonb',
            isNullable: true,
          },
          {
            name: 'created_at',
            type: 'timestamp',
            default: 'now()',
          },
        ],
      }),
      true,
    );
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.dropTable('users');
  }
}

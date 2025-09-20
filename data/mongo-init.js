// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the resume_analyzer database
db = db.getSiblingDB('resume_analyzer');

// Create collections with validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['email', 'full_name', 'role', 'hashed_password'],
      properties: {
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        },
        full_name: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 100
        },
        role: {
          enum: ['hr', 'candidate']
        },
        hashed_password: {
          bsonType: 'string'
        }
      }
    }
  }
});

db.createCollection('jobs', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['title', 'description', 'company', 'location', 'job_type', 'experience_level', 'hr_id'],
      properties: {
        title: {
          bsonType: 'string',
          minLength: 3,
          maxLength: 200
        },
        description: {
          bsonType: 'string',
          minLength: 50,
          maxLength: 5000
        },
        company: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 100
        },
        location: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 100
        },
        job_type: {
          enum: ['full_time', 'part_time', 'contract', 'internship', 'remote']
        },
        experience_level: {
          enum: ['entry', 'junior', 'mid', 'senior', 'lead', 'executive']
        }
      }
    }
  }
});

db.createCollection('resumes', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['candidate_id', 'filename', 'file_path', 'file_type', 'file_size'],
      properties: {
        candidate_id: {
          bsonType: 'string'
        },
        filename: {
          bsonType: 'string'
        },
        file_path: {
          bsonType: 'string'
        },
        file_type: {
          enum: ['pdf', 'docx', 'txt']
        },
        file_size: {
          bsonType: 'number',
          minimum: 0
        },
        status: {
          enum: ['uploaded', 'processing', 'processed', 'failed']
        }
      }
    }
  }
});

db.createCollection('applications');
db.createCollection('candidate_rankings');
db.createCollection('resume_analysis');
db.createCollection('skill_recommendations');

// Create indexes for better performance
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ role: 1 });

db.jobs.createIndex({ hr_id: 1 });
db.jobs.createIndex({ status: 1 });
db.jobs.createIndex({ title: 'text', description: 'text', company: 'text' });

db.resumes.createIndex({ candidate_id: 1 });
db.resumes.createIndex({ status: 1 });

db.applications.createIndex({ job_id: 1 });
db.applications.createIndex({ candidate_id: 1 });
db.applications.createIndex({ status: 1 });

db.candidate_rankings.createIndex({ job_id: 1 });
db.candidate_rankings.createIndex({ candidate_id: 1 });

db.resume_analysis.createIndex({ resume_id: 1 });
db.resume_analysis.createIndex({ candidate_id: 1 });

db.skill_recommendations.createIndex({ candidate_id: 1 });

print('Database initialization completed successfully!');

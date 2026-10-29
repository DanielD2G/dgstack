// Sessions live in process memory. The ALB uses sticky sessions so a user
// keeps hitting the same instance.
const store = new Map();

module.exports = {
  get: (sid) => store.get(sid),
  set: (sid, value) => store.set(sid, value),
  del: (sid) => store.delete(sid),
};
